DCS input restore
==================

Convert DCS joystick profiles from a previous install.

Useful for when you reinstall windows or move DCS to a new rig
and don't want to manually re-create all of your input profiles.

Suggested use
------------------

Make sure your old input DCS saved games directory is still at `%USERPROFILE%\Saved Games\DCS`.
Then run DCS on your new Windows install. This will generate a
new dcs.log file that contains the new joystick device profile
names. 

Then run once with no arguments:

```
python dcs_input_restore.py
```

This will print out a list of files that will be renamed.  If you
are happy with these actions, then re-run with the -x options:

```
python dcs_input_restore.py -x
```
If you're using **DCS** ***OpenBeta*** run the program with the -ob option:

```
python dcs_input_restore.py -x -ob
```

**Reccomend you make a backup of your DCS input directory before running the above step.**
