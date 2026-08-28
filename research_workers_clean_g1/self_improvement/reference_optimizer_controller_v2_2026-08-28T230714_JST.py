import sqlite3, os, sys, json, signal, hashlib, subprocess, tempfile
CTRL_SCHEMA='''
CREATE TABLE IF NOT EXISTS attempt(id TEXT PRIMARY KEY,state TEXT NOT NULL,incumbent TEXT NOT NULL,restore_ptr TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS forecast(id INTEGER PRIMARY KEY AUTOINCREMENT,attempt_id TEXT,digest TEXT UNIQUE,payload TEXT);
CREATE TABLE IF NOT EXISTS switch_decision(attempt_id TEXT PRIMARY KEY,state TEXT NOT NULL,forecast_digest TEXT NOT NULL,candidate TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS eval_intent(eval_id TEXT PRIMARY KEY,attempt_id TEXT,candidate TEXT,state TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS outcome(eval_id TEXT PRIMARY KEY,candidate TEXT,score REAL NOT NULL);
'''
PROV_SCHEMA='''
CREATE TABLE IF NOT EXISTS effect(rowid2 INTEGER PRIMARY KEY AUTOINCREMENT, eval_id TEXT, candidate TEXT, score REAL);
CREATE TABLE IF NOT EXISTS call_log(rowid2 INTEGER PRIMARY KEY AUTOINCREMENT, eval_id TEXT, kind TEXT);
'''
def con(path):
    c=sqlite3.connect(path); c.execute('PRAGMA journal_mode=WAL'); c.execute('PRAGMA synchronous=FULL'); return c
def init(ctrl,prov):
    c=con(ctrl); c.executescript(CTRL_SCHEMA); c.commit(); c.close(); p=con(prov); p.executescript(PROV_SCHEMA); p.commit(); p.close()
def kill_if(point,want):
    if point==want: os.kill(os.getpid(), signal.SIGKILL)
def provider_execute(prov,eval_id,candidate,mode):
    p=con(prov); p.execute('INSERT INTO call_log(eval_id,kind) VALUES(?,?)',(eval_id,'execute'))
    if mode=='reconcilable':
        row=p.execute('SELECT score FROM effect WHERE eval_id=? LIMIT 1',(eval_id,)).fetchone()
        if row is None:
            score=0.95; p.execute('INSERT INTO effect(eval_id,candidate,score) VALUES(?,?,?)',(eval_id,candidate,score))
        else: score=row[0]
    else:
        score=0.95; p.execute('INSERT INTO effect(eval_id,candidate,score) VALUES(?,?,?)',(eval_id,candidate,score))
    p.commit(); p.close(); return score
def provider_reconcile(prov,eval_id):
    p=con(prov); p.execute('INSERT INTO call_log(eval_id,kind) VALUES(?,?)',(eval_id,'reconcile')); row=p.execute('SELECT score,candidate FROM effect WHERE eval_id=? ORDER BY rowid2 LIMIT 1',(eval_id,)).fetchone(); p.commit(); p.close(); return row
def run(ctrl,prov,mode,killpoint='none'):
    init(ctrl,prov); c=con(ctrl); aid='attempt-1'
    c.execute("INSERT OR IGNORE INTO attempt(id,state,incumbent,restore_ptr) VALUES(?,?,?,?)",(aid,'RUNNING','direct-v1','artifact://direct-v1')); c.commit()
    kill_if(killpoint,'before_reforecast')
    payload=json.dumps({'elapsed':10,'p_current':0.2,'p_alt':0.9},sort_keys=True); dg=hashlib.sha256(payload.encode()).hexdigest()
    c.execute('INSERT OR IGNORE INTO forecast(attempt_id,digest,payload) VALUES(?,?,?)',(aid,dg,payload)); c.commit()
    kill_if(killpoint,'after_reforecast_persisted')
    c.execute("INSERT OR IGNORE INTO switch_decision(attempt_id,state,forecast_digest,candidate) VALUES(?,?,?,?)",(aid,'AUTHORIZED',dg,'transversal-v1')); c.commit()
    eid='eval-transversal-v1'
    c.execute("INSERT OR IGNORE INTO eval_intent(eval_id,attempt_id,candidate,state) VALUES(?,?,?,?)",(eid,aid,'transversal-v1','INTENT')); c.commit()
    kill_if(killpoint,'before_alternative_dispatch')
    row=c.execute('SELECT 1 FROM outcome WHERE eval_id=?',(eid,)).fetchone()
    if not row:
        st=c.execute('SELECT state FROM eval_intent WHERE eval_id=?',(eid,)).fetchone()[0]
        if mode=='neither' and st=='INTENT':
            if killpoint=='resume':
                c.execute("UPDATE eval_intent SET state='UNKNOWN' WHERE eval_id=?",(eid,)); c.execute("UPDATE attempt SET state='BLOCKED_UNKNOWN' WHERE id=?",(aid,)); c.commit(); c.close(); return 'UNKNOWN'
        if mode=='reconcilable':
            rr=provider_reconcile(prov,eid)
            if rr is not None: score=rr[0]
            else: score=provider_execute(prov,eid,'transversal-v1',mode)
        else:
            score=provider_execute(prov,eid,'transversal-v1',mode)
        kill_if(killpoint,'after_alternative_provider_effect_before_local_outcome')
        c.execute('INSERT OR IGNORE INTO outcome(eval_id,candidate,score) VALUES(?,?,?)',(eid,'transversal-v1',score)); c.execute("UPDATE eval_intent SET state='COMPLETE' WHERE eval_id=?",(eid,)); c.commit()
    score=c.execute('SELECT score FROM outcome WHERE eval_id=?',(eid,)).fetchone()[0]
    if score>=0.9:
        c.execute("UPDATE attempt SET incumbent='transversal-v1',restore_ptr='artifact://transversal-v1',state='COMPLETE' WHERE id=?",(aid,)); c.execute("UPDATE switch_decision SET state='APPLIED' WHERE attempt_id=?",(aid,)); c.commit()
    c.close(); return 'COMPLETE'
def inspect(ctrl,prov):
    c=con(ctrl); p=con(prov)
    a=c.execute('SELECT state,incumbent,restore_ptr FROM attempt').fetchone(); intents=c.execute('SELECT eval_id,state FROM eval_intent').fetchall(); outs=c.execute('SELECT eval_id,candidate,score FROM outcome').fetchall(); fs=c.execute('SELECT count(*) FROM forecast').fetchone()[0]; sw=c.execute('SELECT state FROM switch_decision').fetchone()
    effects=p.execute('SELECT eval_id,candidate,score FROM effect').fetchall(); calls=p.execute('SELECT eval_id,kind,count(*) FROM call_log GROUP BY eval_id,kind ORDER BY eval_id,kind').fetchall(); c.close(); p.close()
    return {'attempt':a,'intents':intents,'outcomes':outs,'forecast_rows':fs,'switch_state':sw[0] if sw else None,'effects':effects,'calls':calls}
def child():
    run(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
def test():
    report={'schema_version':1,'cases':[]}
    for kp in ['before_reforecast','after_reforecast_persisted','before_alternative_dispatch','after_alternative_provider_effect_before_local_outcome']:
        td=tempfile.mkdtemp(); ctrl=td+'/c.db'; prov=td+'/p.db'; init(ctrl,prov)
        proc=subprocess.run([sys.executable,__file__,'child',ctrl,prov,'reconcilable',kp])
        mid=inspect(ctrl,prov); status=run(ctrl,prov,'reconcilable','none'); fin=inspect(ctrl,prov)
        execute=sum(n for e,k,n in fin['calls'] if k=='execute'); effects=len(fin['effects'])
        ok=(status=='COMPLETE' and fin['attempt'][1]=='transversal-v1' and effects==1 and execute==1)
        report['cases'].append({'mode':'reconcilable','killpoint':kp,'child_returncode':proc.returncode,'mid':mid,'final':fin,'pass':ok})
    for nkp, expected_effects, expected_execute in [('before_alternative_dispatch',0,0),('after_alternative_provider_effect_before_local_outcome',1,1)]:
        td=tempfile.mkdtemp(); ctrl=td+'/c.db'; prov=td+'/p.db'; init(ctrl,prov)
        proc=subprocess.run([sys.executable,__file__,'child',ctrl,prov,'neither',nkp])
        mid=inspect(ctrl,prov); status=run(ctrl,prov,'neither','resume'); fin=inspect(ctrl,prov)
        execute=sum(n for e,k,n in fin['calls'] if k=='execute'); reconcile=sum(n for e,k,n in fin['calls'] if k=='reconcile')
        ok=(status=='UNKNOWN' and fin['attempt'][0]=='BLOCKED_UNKNOWN' and fin['attempt'][1]=='direct-v1' and len(fin['effects'])==expected_effects and execute==expected_execute and reconcile==0 and len(fin['outcomes'])==0)
        report['cases'].append({'mode':'neither','killpoint':nkp,'child_returncode':proc.returncode,'mid':mid,'final':fin,'pass':ok})
    report['all_passed']=all(x['pass'] for x in report['cases'])
    open('/tmp/optimizer_controller_v2_report.json','w').write(json.dumps(report,indent=2,sort_keys=True))
    print(json.dumps({'all_passed':report['all_passed'],'cases':[{'mode':x['mode'],'killpoint':x['killpoint'],'pass':x['pass'],'final_attempt':x['final']['attempt'],'calls':x['final']['calls'],'effects':len(x['final']['effects'])} for x in report['cases']]},indent=2))
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='child': child()
    else: test()
