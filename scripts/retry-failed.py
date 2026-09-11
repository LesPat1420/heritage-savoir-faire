#!/usr/bin/env python3
"""Reessaie l'upload d'une liste de fichiers en echec (un chemin distant
relatif a la racine du site par ligne, ex: www/assets/img/foo.jpg), avec
plus de patience que le script principal (utile quand OVH est instable
pendant une rafale de connexions/deconnexions)."""
import os, sys, stat, time, paramiko

HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL_ROOT = os.path.dirname(HERE)
ENV_FILE = os.path.join(LOCAL_ROOT, ".deploy", "ftp-credentials.env")


def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def remote_mkdir_p(sftp, path):
    parts = path.split("/")
    cur = ""
    for p in parts:
        cur = p if not cur else cur + "/" + p
        try:
            sftp.stat(cur)
        except FileNotFoundError:
            sftp.mkdir(cur)


def main():
    list_file = sys.argv[1] if len(sys.argv) > 1 else None
    if not list_file or not os.path.exists(list_file):
        print("Usage: retry-failed.py <fichier-liste-chemins-distants>")
        return 1
    with open(list_file) as f:
        remote_paths = [l.strip() for l in f if l.strip()]

    env = load_env(ENV_FILE)
    host = env["OVH_HOST"]
    port = int(env.get("OVH_PORT", "22"))
    user = env["OVH_USER"]
    password = env["OVH_PASS"]
    remote_root = env.get("OVH_REMOTE_ROOT", "www")

    def connect():
        tr = paramiko.Transport((host, port))
        tr.connect(username=user, password=password)
        return tr, paramiko.SFTPClient.from_transport(tr)

    t, sftp = connect()

    n_up = n_err = 0
    failed = []
    delays = [2, 5, 10, 20, 30]

    for remote_path in remote_paths:
        rel = remote_path[len(remote_root) + 1:] if remote_path.startswith(remote_root + "/") else remote_path
        local_path = os.path.join(LOCAL_ROOT, rel.replace("/", os.sep))
        if not os.path.exists(local_path):
            print("MANQUANT EN LOCAL:", local_path)
            failed.append(remote_path)
            continue

        remote_dir = os.path.dirname(remote_path)
        ok = False
        last_err = None
        for attempt, delay in enumerate(delays):
            try:
                remote_mkdir_p(sftp, remote_dir)
                try:
                    lst = sftp.lstat(remote_path)
                    if stat.S_ISLNK(lst.st_mode):
                        sftp.remove(remote_path)
                except FileNotFoundError:
                    pass
                sftp.put(local_path, remote_path, confirm=False)
                time.sleep(1.0)
                remote_size = sftp.stat(remote_path).st_size
                local_size = os.path.getsize(local_path)
                if remote_size != local_size:
                    time.sleep(2.0)
                    remote_size = sftp.stat(remote_path).st_size
                if remote_size != local_size:
                    raise IOError(f"taille distante {remote_size} != locale {local_size}")
                ok = True
                break
            except Exception as e:
                last_err = e
                print(f"  echec tentative {attempt+1} pour {remote_path} : {e}")
                try:
                    sftp.close(); t.close()
                except Exception:
                    pass
                time.sleep(delay)
                t, sftp = connect()
        if ok:
            n_up += 1
            print("OK", remote_path)
        else:
            n_err += 1
            failed.append(remote_path)
            print("ERREUR DEFINITIVE", remote_path, ":", last_err)

    print(f"\nTermine : {n_up} envoyes, {n_err} en echec.")
    if failed:
        print("Toujours en echec :")
        for p in failed:
            print(" ", p)
    sftp.close()
    t.close()
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
