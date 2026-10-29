#!/usr/bin/env python3
"""Independently verify the stored quartic P4-incidence exclusion.

Regenerate the Boolean premises, check every additional edge clause against
explicit graph rules, then replay the positive-hint RUP contradiction. Earlier
small-edge classifications and the named quartic lemmas remain premises.
"""
import argparse
from collections import Counter
import json
import lzma
from pathlib import Path
import time

from full35_compatibility import TemplateFamily, require
from quartic_path_cnf import formula
from quartic_path_projection import project_quartic_structure
from quartic_square_profiles import prefix as square_prefix
from verify_branch_refutation import (Bounds, Contradiction, Interval, force,
    forbid, normalise, verify_trace, verify_certificate)
from verify_positive_rup import verify as verify_rup


def read_json(path):
    path=Path(path)
    opener=lzma.open if path.suffix=='.xz' else open
    with opener(path,'rt',encoding='utf-8') as stream:return json.load(stream)


def root_prefix():
    # The original SAT encoding fixes only radius-two incidences. Its larger
    # family includes our canonical P4 root; q proves the missing corner edge.
    result=square_prefix(13)
    for v in range(5,26):result[2+v]&=31
    return result


def validate_trace(trace):
    require(isinstance(trace,list)and len(trace)<=26,'Invalid trace')
    require(all(isinstance(step,list)and len(step)==2
                and step[0]in('delete','eliminate')
                and type(step[1])is int and 0<=step[1]<26 for step in trace),
            'Invalid trace step')


def verify_graph_clause(clause,proof,root,edges,family):
    require(isinstance(proof,dict)and set(proof)=={'q','terminal'},'Invalid graph-clause proof')
    q=proof['q'];terminal=proof['terminal']
    require(type(q)is int and 0<=q<=650,'Invalid projection count')
    require(isinstance(terminal,list)and terminal,'Missing terminal')
    tag=terminal[0]
    if tag in ('x','q'):require(len(terminal)==1,'Invalid local terminal')
    elif tag in ('r','35'):
        require(len(terminal)==2,'Invalid trace terminal');validate_trace(terminal[1])
    elif tag=='b':
        require(len(terminal)==2 and isinstance(terminal[1],dict),'Invalid branch terminal')
        require(terminal[1].get('format')in tuple(f'52-edge-branch-refutation-v{v}'for v in(1,2,3,4)),
                'The P4 subfamily proof must use original independent rules')
    else:raise ValueError('Unknown graph terminal')
    require(all(type(literal)is int and 0<abs(literal)<=len(edges)for literal in clause),
            'A nonlogical input must be an edge clause')
    state=Interval(root)
    try:
        for literal in clause:
            u,v=edges[abs(literal)-1]
            (forbid if literal>0 else force)(state.known,state.possible,u,v)
        for _ in range(q):
            normalise(state.known,state.possible,state.upper)
            require(project_quartic_structure(state.known,state.possible,state.upper)>0,
                    'A supplied projection makes no change')
        normalise(state.known,state.possible,state.upper)
        if tag=='q':
            project_quartic_structure(state.known,state.possible,state.upper)
            raise ValueError('The supplied quartic terminal does not refute the family')
        if tag=='x':raise ValueError('The supplied local terminal does not refute the family')
        if tag=='r':
            verify_trace(state.known,state.possible,state.upper,terminal[1])
            return {'kind':'r'}
        if tag=='35':
            bounds=Bounds.from_family(state.known,state.possible,state.upper)
            for operation,vertex in terminal[1]:
                bounds.tighten();bounds.step(operation,vertex)
            bounds.tighten()
            possible,nodes=family.possible(bounds)
            require(not possible,'A full35 obstruction remains compatible')
            return {'kind':'35','embedding_nodes':nodes}
        # The stored ordinary proof may forget forbidden edges, but it may not
        # add an assumption: its known edges are exactly the proved ones.
        expected=[26,5]+[sum(1<<v for v in row)for row in state.known]
        larger=Interval(expected)
        require(all(state.possible[v]<=larger.possible[v]for v in range(26)),
                'Subfamily proof does not cover all current possible edges')
        try:
            verify_certificate(terminal[1],expected)
        except Contradiction as exc:
            raise ValueError('Unexpected unhandled branch-checker contradiction') from exc
        return {'kind':'b'}
    except Contradiction:
        return {'kind':'local' if tag=='x' else tag,'early_contradiction':True}


_WORKER = None


def _initialize_graph_worker(repository, root, edges):
    global _WORKER
    _WORKER = (root, edges, TemplateFamily(repository))


def _verify_graph_worker(index, clause, proof):
    root, edges, family = _WORKER
    return index, verify_graph_clause(clause, proof, root, edges, family)


def graph_results(indices, inputs, proofs, repository, root, edges, workers):
    """Freshly verify every requested clause; bound queued jobs and retain no cache."""
    require(type(workers) is int and workers >= 1, 'Worker count must be positive')
    if workers == 1:
        family = TemplateFamily(repository)
        for index in indices:
            yield index, verify_graph_clause(inputs[index], proofs[index], root, edges, family)
        return
    from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
    iterator = iter(indices)
    with ProcessPoolExecutor(max_workers=workers, initializer=_initialize_graph_worker,
                             initargs=(str(repository), root, edges)) as pool:
        pending = {}
        def submit():
            index = next(iterator, None)
            if index is None:
                return False
            future = pool.submit(_verify_graph_worker, index, inputs[index], proofs[index])
            pending[future] = index
            return True
        for _ in range(2 * workers):
            if not submit():
                break
        while pending:
            completed, _ = wait(pending, return_when=FIRST_COMPLETED)
            for future in completed:
                expected = pending.pop(future)
                index, result = future.result()
                require(type(index) is int and index == expected, 'Wrong parallel clause result')
                yield index, result
                submit()


def verify(rup,theory,repository,progress=None,workers=1):
    require(type(workers)is int and workers>=1,'Worker count must be positive')
    require(isinstance(theory,dict)and theory.get('format')=='quartic-p4-theory-v1',
            'Unknown P4 theory format')
    root=root_prefix()
    require(theory.get('root')==root,'Wrong P4 root')
    # This validates every clause, literal and hint before premise matching.
    input_count,step_count=verify_rup(rup)
    cnf,edges,_=formula(root[2:])
    require(rup['variables']==cnf.variables,'Wrong Boolean variable universe')
    logical={tuple(clause)for clause in cnf.clauses}
    missing={index for index,clause in enumerate(rup['inputs'])if tuple(clause)not in logical}
    records=theory.get('proofs')
    require(isinstance(records,list),'Missing graph proofs')
    by_index={}
    for record in records:
        require(isinstance(record,dict)and set(record)=={'input','proof'},'Invalid graph-proof record')
        index=record['input']
        require(type(index)is int and index in missing and index not in by_index,
                'Unknown, redundant or duplicate graph-proof index')
        by_index[index]=record['proof']
    require(set(by_index)==missing,'Some Boolean inputs lack an independent graph proof')
    stats=Counter();embedding_nodes=0;checked=set()
    for index,result in graph_results(sorted(missing),rup['inputs'],by_index,
                                      repository,root,edges,workers):
        require(index in missing and index not in checked,'Unexpected or duplicate verified clause')
        checked.add(index)
        stats[result['kind']]+=1;embedding_nodes+=result.get('embedding_nodes',0)
        if progress and len(checked)%512==0:progress(len(checked),len(missing),dict(stats))
    require(checked==missing,'Incomplete graph-clause verification')
    return {'status':'PASS-relative-to-named-prior-lemmas','logical_inputs':input_count-len(missing),
            'graph_inputs':len(missing),'rup_steps':step_count,'theory_terminals':dict(stats),
            'embedding_nodes':embedding_nodes,'workers':workers,'scope':'quartic P4-incidence minimum-counterexample exclusion'}


def main():
    repository=Path(__file__).resolve().parents[1]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository',type=Path,default=repository)
    parser.add_argument('--rup',type=Path)
    parser.add_argument('--theory',type=Path)
    parser.add_argument('--workers',type=int,default=1,help='Parallel independent graph-clause checks')
    args=parser.parse_args();started=time.monotonic()
    rup=args.rup or args.repository/'sources/eleven-quartic-p4-rup.json.xz'
    theory=args.theory or args.repository/'sources/eleven-quartic-p4-theory.json.xz'
    def progress(done,total,stats):print(json.dumps({'checked':done,'total':total,'seconds':time.monotonic()-started,'terminals':stats}),flush=True)
    result=verify(read_json(rup),read_json(theory),args.repository,progress,workers=args.workers)
    result['seconds']=time.monotonic()-started;print(json.dumps(result,sort_keys=True))
    print('Premises: minimum-order52 reduction; earlier edge minima and full34/35 classifications; triangle exclusion; square directions; guarded v1 C4 exclusion; marked-H22 and exceptional-square reconstruction.')
    print('This excludes the P4 square-incidence case only, not all remaining quartic cases.')

if __name__=='__main__':main()
