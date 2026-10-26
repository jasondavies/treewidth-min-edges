"""Reproduce f(9)=42: saved-certificate checks, or the full classification.

All work happens in --output; the checkout's reference data are unchanged.
--full regenerates the earlier 28/34-edge classifications as well. Completed
stages are checkpointed. Reuse an output directory only with identical code.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if not __debug__ or os.environ.get('PYTHONOPTIMIZE'):
        raise RuntimeError('Run without Python optimization: assertions check certificates.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=min(16, os.cpu_count() or 1))
    parser.add_argument('--full', action='store_true', help='regenerate every classification, including k<=8')
    parser.add_argument('--genreg-source', type=Path, help='directory containing GENREG r5 sources; required for --full')
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('--workers must be positive')
    if args.full and args.genreg_source is None:
        parser.error('--full requires --genreg-source')
    if args.genreg_source:
        args.genreg_source = args.genreg_source.resolve()
        for name in ('gendef.h', 'genreg.c', 'main.c', 'optmid.c'):
            if not (args.genreg_source/name).is_file():
                parser.error(f'missing GENREG file: {name}')
    work = args.output.resolve()
    if work == ROOT or ROOT in work.parents:
        parser.error('choose an output directory outside this checkout')
    work.mkdir(parents=True, exist_ok=True)
    source_files = sorted(p for directory in ('scripts','sources') for p in (ROOT/directory).rglob('*')
                          if p.is_file() and '__pycache__' not in p.parts)
    signature = {str(p.relative_to(ROOT)):sha(p) for p in source_files}
    config = {'files':signature, 'full':args.full, 'workers':args.workers,
              'genreg':({name:sha(args.genreg_source/name) for name in
                         ('gendef.h','genreg.c','main.c','optmid.c')} if args.genreg_source else None),
              'CC':os.environ.get('CC','cc'), 'GENG_SOURCE':os.environ.get('GENG_SOURCE','/usr/share/nauty/geng.c')}
    manifest = work/'reproduction-inputs.json'
    if manifest.exists():
        if json.loads(manifest.read_text()) != config:
            raise RuntimeError('Inputs/options changed; choose a new output directory.')
    else:
        if any(work.iterdir()):
            raise RuntimeError('New output directory must be empty.')
        for directory in ('scripts','sources'):
            shutil.copytree(ROOT/directory, work/directory, ignore=shutil.ignore_patterns('__pycache__'))
        manifest.write_text(json.dumps(config,indent=2)+'\n')
    steps = work/'steps'; steps.mkdir(exist_ok=True)
    results = work/'runs'; results.mkdir(exist_ok=True)
    data = work/'sources/nine'
    workers = ['--workers', str(args.workers)]

    def step(name, script, *arguments):
        marker = steps/(name+'.json')
        if marker.exists():
            print('Already complete:', name, flush=True)
            return
        command = [sys.executable, str(work/'scripts'/script), *map(str,arguments)]
        print('\nRunning:', name, flush=True)
        subprocess.run(command, cwd=work, check=True)
        marker.write_text(json.dumps({'command':command})+'\n')

    def check_count(directory, key, expected):
        report = json.loads((results/directory/'summary.json').read_text())
        assert report[key] == expected, (directory,key,report[key],expected)

    def install(source, name):
        shutil.copy2(source, data/name)

    def compare(source, name):
        assert source.read_bytes() == (ROOT/'sources/nine'/name).read_bytes(), name

    def rounds(name, script, *arguments):
        # Timed-out partitions are retried from their start. Double the allowance
        # on each round so a slow machine cannot loop forever at a fixed limit.
        allowance = 180
        directory = results/name
        while True:
            if (directory/'summary.json').exists():
                if json.loads((directory/'summary.json').read_text())['status']=='complete':
                    break
            command = [sys.executable,str(work/'scripts/nine'/script), '--output',str(directory),
                       *workers,'--case-seconds',str(allowance),'--round-seconds',str(allowance),
                       *map(str,arguments)]
            subprocess.run(command,cwd=work,check=True)
            allowance *= 2

    step('witness','nine/check_treewidth_nine_witness.py')
    if args.full:
        step('base28','reproduce.py')
        step('base34','reproduce_uniqueness.py','--quartic-generator','genreg',
             '--genreg-source',args.genreg_source,*workers)
        # Adapt the freshly regenerated base enumeration to the subsequent classifier.
        base = json.loads((work/'sources/uniqueness.json').read_text())
        core29 = results/'base29'; core29.mkdir(exist_ok=True)
        quartic17 = results/'base17'; quartic17.mkdir(exist_ok=True)
        seeds = [s for row in base['cores29'] for s in row['exceptions']]
        assert len(seeds)==124
        (core29/'n0-part-0.g6').write_text('\n'.join(seeds)+'\n')
        (core29/'summary.json').write_text(json.dumps({'status':'complete','retained':124}))
        q=base['quartic17']; assert q['total']==86221634 and q['counterexamples']==1
        (quartic17/'part-0.g6').write_text('\n'.join(q['exceptions'])+'\n')
        (quartic17/'summary.json').write_text(json.dumps({'status':'complete','leaves':q['total'],'negative':1}))
        step('residues34','nine/classify_treewidth34.py','--cores29',core29,
             '--quartic17',quartic17,'--output',results/'classify34')
        for suffix in ('29','34'):
            source=results/f'classify34/family{suffix}.g6'
            compare(source,f'treewidth34-family{suffix}.g6')
            install(source,f'treewidth34-family{suffix}.g6')
        step('prefix-audit','nine/audit_prefix.py')
        step('genreg-audit','nine/audit_genreg_treewidth.py','--source',args.genreg_source)
        step('small21','nine/check_treewidth21_classification.py','--output',results/'small21')
        step('girth19','nine/check_treewidth_nine_girth5.py')
        rounds('core30','run_treewidth30_cores.py','--parts',128)
        check_count('core30','retained',13206)
        cores=sorted(s for p in (results/'core30').glob('n*-part-*.g6') for s in p.read_text().splitlines())
        (data/'treewidth30-cores.g6').write_text('\n'.join(cores)+'\n')
        install(results/'core30/summary.json','treewidth30-core-results.json')
        step('classify35','nine/classify_treewidth35.py','--cores',results/'core30','--output',results/'classify35')
        for suffix in ('30','35'):
            source=results/f'classify35/family{suffix}.g6'
            compare(source,f'treewidth35-family{suffix}.g6')
            install(source,f'treewidth35-family{suffix}.g6')
        step('quartic-residues','nine/classify_treewidth30_quartic.py','--cores',results/'core30',
             '--output',results/'quartic-residues')
        source=results/'quartic-residues/family.g6'
        compare(source,'treewidth30-quartic-family.g6'); install(source,'treewidth30-quartic-family.g6')
        step('classify35-all','nine/classify_treewidth35_all.py','--output',results/'classify35-all')
        source=results/'classify35-all/family.g6'
        compare(source,'treewidth35-all-family.g6'); install(source,'treewidth35-all-family.g6')
        rounds('quartic20','run_genreg_no_four_cycles.py','--source',args.genreg_source,
               '--vertices',20,'--degree',4,'--width',8,'--cap',1,'--cover','--parts',64)
        check_count('quartic20','negative',0)
        step('broad30','nine/classify_treewidth30_broad.py','--output',results/'broad30')
        check_count('broad30','family',73517)
        rounds('core31','run_treewidth31_cores_pruned.py','--parts',256)
        check_count('core31','retained',882135)
        rounds('quartic18','run_genreg_treewidth.py','--source',args.genreg_source,
               '--vertices',18,'--degree',4,'--width',7,'--cover','--parts',1024)
        check_count('quartic18','negative',413)
        step('classify31','nine/classify_treewidth31.py','--cores',results/'core31',
             '--family30',results/'broad30/family.g6','--output',results/'classify31',*workers)
        check_count('classify31','family',4539644)
        step('classify36','nine/classify_treewidth36.py','--family30',results/'broad30/family.g6',
             '--family31',results/'classify31/family.g6','--quartic18',results/'quartic18',
             '--output',results/'classify36',*workers)
        source=results/'classify36/family.g6'
        compare(source,'treewidth36-family.g6'); install(source,'treewidth36-family.g6')
        step('extensions41-c','nine/check_treewidth41_extensions.py','--family',source,
             '--output',results/'extensions41-c',*workers)
        check_count('extensions41-c','candidates',0)

    step('high-degrees','nine/check_high_degrees.py','--output',results/'high-degrees',*workers)
    step('codegree-three','nine/check_treewidth40_quartic_codegree.py')
    step('extensions40','nine/audit_treewidth40_final_extensions.py',
         '--family35',data/'treewidth35-family.g6','--quartic',data/'treewidth30-quartic-family.g6',
         '--output',results/'extensions40',*workers)
    check_count('extensions40','families',{'five':72751,'four-cycle':1062270})
    step('extensions41','nine/audit_treewidth41_extensions.py','--family',data/'treewidth36-family.g6',
         '--output',results/'extensions41',*workers)
    check_count('extensions41','extensions',22489604)
    result={'status':'complete','mode':'full' if args.full else 'saved-family certificates',
            'minimum_edges':42 if args.full else None,
            'note':'Saved-family mode does not prove completeness of the classifications.'}
    (work/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: '+('full reproduction of f(9)=42.' if args.full else
                   'witness and final certificates; classification completeness was not rerun.'),flush=True)


if __name__=='__main__':
    main()
