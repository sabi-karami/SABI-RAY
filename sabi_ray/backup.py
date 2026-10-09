'''Consistent SQLite backup. Run on the deployed host, not via a public API.'''
import argparse,datetime,os,pathlib,sqlite3

def backup(source,destination):
    source=pathlib.Path(source).resolve();destination=pathlib.Path(destination).resolve()
    if source==destination or destination.exists():raise ValueError('Destination must be a new file')
    if not source.is_file():raise FileNotFoundError('Database not found')
    destination.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(destination,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
    try:
        with sqlite3.connect(source.as_uri()+'?mode=ro',uri=True) as src, sqlite3.connect(destination) as dst:
            src.backup(dst)
            if dst.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise RuntimeError('Backup integrity check failed')
    except BaseException:
        destination.unlink(missing_ok=True);raise
    return destination
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',default='/var/lib/pasarguard/db.sqlite3');parser.add_argument('--output',required=True);args=parser.parse_args()
    backup(args.source,args.output);print('SQLite backup verified. Store the complete volume backup separately and securely.')
