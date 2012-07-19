scaleupbrazil/captricity
========================

This directory has scripts related to using Captricity to convert scanned survey forms into datasets for analysis.

The Captricity API token should be in a file called .captricity-token, which should be kept in this directory.

The scripts will assume that there is a (not-versioned) directory called test-data/. Since it wouldn't be appropriate for us to put scanned survey forms in the public repository, we suggest putting the test forms somewhere else on your computer and creating a symlink to that directory using

% ln -s /path/to/test/forms test-data

