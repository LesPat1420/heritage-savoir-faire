#!/usr/bin/env python3
"""Deploie le site sur l'hebergement OVH (etudesbois.fr) par SFTP.

Identifiants lus depuis .deploy/ftp-credentials.env (gitignore, jamais commite) :
  OVH_HOST, OVH_PORT, OVH_USER, OVH_PASS, OVH_REMOTE_ROOT

Usage :
  pip3 install --user paramiko   # une fois
  python3 scripts/deploy-ovh.py

Envoie tout le dossier du site sauf : .git/, _dossier-lou/ (prive, jamais publie),
scripts/, .deploy/, les apercus de maquettes (apercu-*.png), README.md.
Remplace tout lien symbolique deja present cote serveur (ex: www/index.html
qui pointe par defaut vers la page de bienvenue OVH) plutot que d'ecrire au
travers.
"""
import os, sys, stat, time, paramiko

HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL_ROOT = os.path.dirname(HERE)
ENV_FILE = os.path.join(LOCAL_ROOT, ".deploy", "ftp-credentials.env")

EXCLUDE_DIRS = {".git", "_dossier-lou", "scripts", ".deploy"}
EXCLUDE_FILES_PREFIX = ("apercu-",)
EXCLUDE_FILES = {"README.md", ".gitignore", ".nojekyll"}


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
    if not os.path.exists(ENV_FILE):
        print(f"Manquant : {ENV_FILE}\nCree-le avec OVH_HOST/OVH_PORT/OVH_USER/OVH_PASS/OVH_REMOTE_ROOT.")
        return 1
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

    # liste (local_path, remote_dir, fn) a plat : la connexion OVH decroche
    # apres un certain volume, on reconnecte donc periodiquement plutot que
    # de garder une seule session ouverte pendant tout le transfert.
    todo = []
    n_skip = 0
    for dirpath, dirnames, filenames in os.walk(LOCAL_ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        rel_dir = os.path.relpath(dirpath, LOCAL_ROOT)
        remote_dir = remote_root if rel_dir == "." else remote_root + "/" + rel_dir.replace(os.sep, "/")
        for fn in filenames:
            if fn in EXCLUDE_FILES or fn.startswith(EXCLUDE_FILES_PREFIX):
                n_skip += 1
                continue
            todo.append((os.path.join(dirpath, fn), remote_dir, fn))

    n_up = n_err = 0
    bytes_up = 0
    made_dirs = set()
    failed = []
    RECONNECT_EVERY = 60

    for i, (local_path, remote_dir, fn) in enumerate(todo):
        if i and i % RECONNECT_EVERY == 0:
            try:
                sftp.close(); t.close()
            except Exception:
                pass
            time.sleep(1)
            t, sftp = connect()
            made_dirs.clear()

        if remote_dir not in made_dirs:
            remote_mkdir_p(sftp, remote_dir)
            made_dirs.add(remote_dir)

        remote_path = remote_dir + "/" + fn
        ok = False
        for attempt in range(3):
            try:
                try:
                    lst = sftp.lstat(remote_path)
                    if stat.S_ISLNK(lst.st_mode):
                        sftp.remove(remote_path)
                except FileNotFoundError:
                    pass
                # confirm=False : le serveur OVH renvoie parfois un stat perime
                # (taille 0) juste apres l'ecriture, ce que confirm=True (par
                # defaut) prend a tort pour un echec. On verifie nous-memes,
                # avec une petite tolerance de latence.
                sftp.put(local_path, remote_path, confirm=False)
                time.sleep(0.05)
                remote_size = sftp.stat(remote_path).st_size
                local_size = os.path.getsize(local_path)
                if remote_size != local_size:
                    time.sleep(0.5)
                    remote_size = sftp.stat(remote_path).st_size
                if remote_size != local_size:
                    raise IOError(f"taille distante {remote_size} != locale {local_size}")
                ok = True
                break
            except Exception as e:
                last_err = e
                try:
                    sftp.close(); t.close()
                except Exception:
                    pass
                time.sleep(1.5)
                t, sftp = connect()
                made_dirs = {remote_dir}
                remote_mkdir_p(sftp, remote_dir)
        if ok:
            n_up += 1
            bytes_up += os.path.getsize(local_path)
            if n_up % 40 == 0:
                print(f"... {n_up} fichiers envoyes ({bytes_up / 1e6:.1f} Mo)")
        else:
            n_err += 1
            failed.append((local_path, remote_path))
            print("ERREUR", local_path, "->", remote_path, ":", last_err)

    print(f"\nTermine : {n_up} fichiers envoyes ({bytes_up / 1e6:.1f} Mo), {n_skip} ignores, {n_err} erreurs.")
    if failed:
        print("Fichiers en echec :")
        for lp, rp in failed:
            print(" ", rp)
    sftp.close()
    t.close()
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
