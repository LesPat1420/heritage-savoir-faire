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
import os, sys, stat, paramiko

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

    t = paramiko.Transport((host, port))
    t.connect(username=user, password=password)
    sftp = paramiko.SFTPClient.from_transport(t)

    n_up = n_skip = n_err = 0
    bytes_up = 0
    for dirpath, dirnames, filenames in os.walk(LOCAL_ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        rel_dir = os.path.relpath(dirpath, LOCAL_ROOT)
        remote_dir = remote_root if rel_dir == "." else remote_root + "/" + rel_dir.replace(os.sep, "/")
        remote_mkdir_p(sftp, remote_dir)
        for fn in filenames:
            if fn in EXCLUDE_FILES or fn.startswith(EXCLUDE_FILES_PREFIX):
                n_skip += 1
                continue
            local_path = os.path.join(dirpath, fn)
            remote_path = remote_dir + "/" + fn
            try:
                try:
                    lst = sftp.lstat(remote_path)
                    if stat.S_ISLNK(lst.st_mode):
                        sftp.remove(remote_path)
                except FileNotFoundError:
                    pass
                sftp.put(local_path, remote_path)
                n_up += 1
                bytes_up += os.path.getsize(local_path)
                if n_up % 40 == 0:
                    print(f"... {n_up} fichiers envoyes ({bytes_up / 1e6:.1f} Mo)")
            except Exception as e:
                n_err += 1
                print("ERREUR", local_path, "->", remote_path, ":", e)

    print(f"\nTermine : {n_up} fichiers envoyes ({bytes_up / 1e6:.1f} Mo), {n_skip} ignores, {n_err} erreurs.")
    sftp.close()
    t.close()
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
