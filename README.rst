mapproxy_cacherotate.py
=======================


``mapproxy_cacherotate`` is a small tool to move cache levels around.
Use it to be able to add or remove zoom levels/resolutions from a MapProxy cache grid without needing to re-seed everything.

The tools runs in *dry-mode* by default and only moves files and directories with the ``--rotate`` option.

NOTE: You should temporarily shutdown MapProxy before rotating files. Don't forget to update the MapProxy grid after rotating and before restarting MapProxy.


Example use case
----------------

You have the following configuration::

    grid:
      mygrid:
        res: [
           #  res         level     scale @90.7 DPI
           28.0000000000, #  0      100000.00000000
            5.6000000000, #  1       20000.00000000
            2.8000000000, #  2       10000.00000000
        ]
        ...

    cache:
      my_cache:
        grids: [mygrid]
        ...

You can add another resolution (14m/px, 1:50.000) by updating the configuration as follows::


    grid:
      mygrid:
        res: [
           #  res         level     scale @90.7 DPI
           28.0000000000, #  0      100000.00000000
           14.0000000000, #  1       50000.00000000
            5.6000000000, #  2       20000.00000000
            2.8000000000, #  3       10000.00000000
        ]
        ...

You now need to remove the existing cache, because otherwise level 1 would use tiles from the old level 1. Removing the cache can be impractical with larger caches and so you can try to "rotate" the existing cached levels (e.g. move level 2 to 1, 1 to 2). ``mapproxy_cacherotate`` automates this process.


If the cache directory looks like this::

    % find cache_data -maxdepth 2
    cache_data
    cache_data/osm_cache_EPSG3857
    cache_data/osm_cache_EPSG3857/00
    cache_data/osm_cache_EPSG3857/01
    cache_data/osm_cache_EPSG3857/02

You can use ``mapproxy_cacherotate`` to see what would happen::

    mapproxy_cacherotate.py cache_data/osm_cache_EPSG3857 --from-level 1

And actually rotate the levels with ::

    mapproxy_cacherotate.py cache_data/osm_cache_EPSG3857 --from-level 1 --rotate

To get::

    % find cache_data -maxdepth 2
    cache_data
    cache_data/osm_cache_EPSG3857
    cache_data/osm_cache_EPSG3857/.last_rotate
    cache_data/osm_cache_EPSG3857/00
    cache_data/osm_cache_EPSG3857/02
    cache_data/osm_cache_EPSG3857/03


The ``.last_rotate`` helps ``mapproxy_cacherotate`` to not rotate multiple times.
You can remove that file with::

    mapproxy_cacherotate.py cache_data/* --remove-locks

You can also do the reverse: remove levels and rename 2 to 1 and 3 to 2::

    mapproxy_cacherotate`` cache_data/* --drop-level 1 --rotate
