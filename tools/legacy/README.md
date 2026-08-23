# Legacy one-off scripts

These are the ad-hoc scripts that were used to bootstrap the translated copies
of the site before it was generated from `src/`. They are kept for reference
only — none of them is part of the build.

`restructure_site.py` used to live in `html/`, which meant it was published as
part of the site and downloadable from the live domain. Moving it here takes it
off the web server.

To rebuild the site, use `python3 tools/build.py` instead.
