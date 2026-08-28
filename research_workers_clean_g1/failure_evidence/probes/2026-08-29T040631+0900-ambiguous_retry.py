import json, sqlite3, tempfile, os, hashlib

class ResponseLost(Exception):
    pass

class IdempotencyMismatch(Exception):
    pass

def setup(path):
    con = sqlite3.connect(path)
    con.execute('PRAGMA journal_mode=WAL')
    con.executescript('''
    CREATE TABLE effects(id INTEGER PRIMARY KEY AUTOINCREMENT, logical_key TEXT NOT NULL, payload TEXT NOT NULL);
    CREATE TABLE idem(token TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, response TEXT NOT NULL);
    ''')
    con.commit(); con.close()

def fp(logical_key, payload):
    return hashlib.sha256((logical_key+'\0'+payload).encode()).hexdigest()

def handle_no_idem(path, logical_key, payload, lose_response=False):
    con = sqlite3.connect(path)
    con.execute('BEGIN IMMEDIATE')
    con.execute('INSERT INTO effects(logical_key,payload) VALUES (?,?)', (logical_key,payload))
    effect_id = con.execute('SELECT last_insert_rowid()').fetchone()[0]
    con.commit(); con.close()
    if lose_response:
        raise ResponseLost('commit happened; response lost')
    return {'effect_id': effect_id}

def handle_idem(path, token, logical_key, payload, lose_response=False):
    fingerprint = fp(logical_key, payload)
    con = sqlite3.connect(path)
    con.execute('BEGIN IMMEDIATE')
    row = con.execute('SELECT fingerprint,response FROM idem WHERE token=?', (token,)).fetchone()
    if row:
        if row[0] != fingerprint:
            con.rollback(); con.close(); raise IdempotencyMismatch('same token, different request')
        response = json.loads(row[1])
        con.commit(); con.close()
        return {'replayed': True, **response}
    con.execute('INSERT INTO effects(logical_key,payload) VALUES (?,?)', (logical_key,payload))
    effect_id = con.execute('SELECT last_insert_rowid()').fetchone()[0]
    response = {'effect_id': effect_id}
    con.execute('INSERT INTO idem(token,fingerprint,response) VALUES (?,?,?)', (token,fingerprint,json.dumps(response,sort_keys=True)))
    con.commit(); con.close()
    if lose_response:
        raise ResponseLost('commit happened; response lost')
    return {'replayed': False, **response}

def count_effects(path):
    con=sqlite3.connect(path)
    n=con.execute('SELECT COUNT(*) FROM effects').fetchone()[0]
    rows=con.execute('SELECT id,logical_key,payload FROM effects ORDER BY id').fetchall()
    con.close(); return n, rows

def scenario_no_idem():
    fd,path=tempfile.mkstemp(); os.close(fd); os.unlink(path); setup(path)
    first=''
    try: handle_no_idem(path,'invoice_42','paid',lose_response=True)
    except ResponseLost as e: first=type(e).__name__
    retry=handle_no_idem(path,'invoice_42','paid',lose_response=False)
    n,rows=count_effects(path); os.unlink(path)
    return {'first_outcome':first,'retry_response':retry,'effect_count':n,'effects':rows}

def scenario_stable_key():
    fd,path=tempfile.mkstemp(); os.close(fd); os.unlink(path); setup(path)
    try: handle_idem(path,'req-42','invoice_42','paid',lose_response=True)
    except ResponseLost: pass
    retry=handle_idem(path,'req-42','invoice_42','paid',lose_response=False)
    n,rows=count_effects(path); os.unlink(path)
    return {'retry_response':retry,'effect_count':n,'effects':rows}

def scenario_rotated_key():
    fd,path=tempfile.mkstemp(); os.close(fd); os.unlink(path); setup(path)
    try: handle_idem(path,'req-42-a','invoice_42','paid',lose_response=True)
    except ResponseLost: pass
    retry=handle_idem(path,'req-42-b','invoice_42','paid',lose_response=False)
    n,rows=count_effects(path); os.unlink(path)
    return {'retry_response':retry,'effect_count':n,'effects':rows}

def scenario_key_parameter_mismatch():
    fd,path=tempfile.mkstemp(); os.close(fd); os.unlink(path); setup(path)
    handle_idem(path,'req-42','invoice_42','paid',lose_response=False)
    mismatch=''
    try: handle_idem(path,'req-42','invoice_43','paid',lose_response=False)
    except IdempotencyMismatch as e: mismatch=type(e).__name__
    n,rows=count_effects(path); os.unlink(path)
    return {'mismatch_outcome':mismatch,'effect_count':n,'effects':rows}

result={
  'probe':'ambiguous_retry_after_commit',
  'scope':'single-process SQLite deterministic application-layer simulation',
  'no_idempotency':scenario_no_idem(),
  'stable_idempotency_key':scenario_stable_key(),
  'rotated_idempotency_key':scenario_rotated_key(),
  'same_key_different_parameters':scenario_key_parameter_mismatch(),
}
print(json.dumps(result, indent=2, sort_keys=True))
