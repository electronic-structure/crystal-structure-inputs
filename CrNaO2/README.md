# QE native
```
pw.x -i pw.in
```

# QE-SIRIUS (default fp64)
```
pw.x -i pw.in -sirius_scf -sirius_cfg cfg64.json
```

# QE-SIRIUS (mixed fp32/fp64)
```
pw.x -i pw.in -sirius_scf -sirius_cfg cfg32-64.json
```
