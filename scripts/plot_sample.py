#!/usr/bin/env python
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import matplotlib.pyplot as plt

from aethernav.coordinates.enu import wgs84_to_enu
from aethernav.datasets.io_vnbd import load_file

p=argparse.ArgumentParser(); p.add_argument('--input', required=True); p.add_argument('--output', required=True); args=p.parse_args()
f=load_file(args.input); enu=wgs84_to_enu(f.latitude.to_numpy(),f.longitude.to_numpy(),f.get('altitude_m',0).to_numpy())
Path(args.output).parent.mkdir(parents=True,exist_ok=True)
fig,ax=plt.subplots(figsize=(8,5)); ax.plot(enu[:,0],enu[:,1],label='reference trajectory',color='#00cfff'); ax.scatter(enu[0,0],enu[0,1],label='start',color='green'); ax.set(xlabel='East (m)',ylabel='North (m)',title='AetherNav sample trajectory'); ax.grid(alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(args.output,dpi=140); print(f'saved {args.output}')
