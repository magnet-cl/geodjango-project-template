#!/bin/bash
# from https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/geolibs/

#django recomended to install this libraries, but I have no idea what they do
sudo apt-get install binutils libproj-dev gdal-bin

# GEOS is a C++ library for performing geometric operations, and is the default
# internal geometry representation used by GeoDjango (it's behind the "lazy"
# geometries). Specifically, the C API library is called (e.g., libgeos_c.so)
# directly from Python using ctypes.
wget http://download.osgeo.org/geos/geos-3.3.5.tar.bz2
tar xjf geos-3.3.5.tar.bz2
cd geos-3.3.5
./configure
make
sudo make install
cd ..
rm -rf geos-3.3.5.tar.bz2
rm -rf geos-3.3.5


#PROJ.4 is a library for converting geospatial data to different coordinate
#reference systems.
wget http://download.osgeo.org/proj/proj-4.8.0.tar.gz
wget http://download.osgeo.org/proj/proj-datumgrid-1.5.tar.gz
# Next, untar the source code archive, and extract the datum shifting files
# in the nad subdirectory. This must be done prior to configuration:
tar xzf proj-4.8.0.tar.gz
cd proj-4.8.0/nad
tar xzf ../../proj-datumgrid-1.5.tar.gz
cd ..
#Finally, configure, make and install PROJ.4:
./configure
make
sudo make install
cd ..
rm -rf proj-4.8.0.tar.gz
rm -rf proj-4.8.0
rm -rf proj-datumgrid-1.5.tar.gz
rm -rf proj-datumgrid-1.5

#!!!GEOS, PROJ.4 and GDAL should be installed prior to building PostGIS

# GDAL is an excellent open source geospatial library that has support for
# reading most vector and raster spatial data formats. Currently, GeoDjango
# only supports GDAL's vector data capabilities [2]. GEOS and PROJ.4 should
# be installed prior to building GDAL.

# First download the latest GDAL release version and untar the archive:
wget http://download.osgeo.org/gdal/gdal-1.9.1.tar.gz
tar xzf gdal-1.9.1.tar.gz
cd gdal-1.9.1
./configure
make
sudo make install
cd ..
rm -rf gdal-1.9.1.tar.gz
rm -rf gdal-1.9.1


# needed by PostGis
# http://www.postgis.org/documentation/manual-2.0/postgis_installation.html
sudo aptitude install postgresql-server-dev-9.1 libxml2-dev

# postgis installation
sudo aptitude install postgis postgresql-9.1-postgis

./install/postgis_template.sh

echo "Add 'django.contrib.gis' to your INSTALLED_APPS"
