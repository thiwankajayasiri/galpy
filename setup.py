from setuptools import setup
from distutils.core import Extension
import sys
import subprocess
import glob

with open('README.rst') as dfile:
    long_description = dfile.read()

# Parse options; current options
# --no-openmp: compile without OpenMP support
# --coverage: compile with gcov support
# --orbit_ext: just compile the orbit extension (for use w/ --coverage)
# --actionAngle_ext: just compile the actionAngle extension (for use w/ --coverage)
# --interppotential_ext: just compile the interppotential extension (for use w/ --coverage)

pot_libraries= ['m','gsl','gslcblas','gomp']
#Option to forego OpenMP
try:
    openmp_pos = sys.argv.index('--no-openmp')
except ValueError:
    extra_compile_args=["-fopenmp"]
else:
    del sys.argv[openmp_pos]
    extra_compile_args= ["-DNO_OMP"]
    pot_libraries.remove('gomp')

#Option to track coverage
try:
    coverage_pos = sys.argv.index('--coverage')
except ValueError:
    extra_link_args= []
else:
    del sys.argv[coverage_pos]
    extra_compile_args.extend(["-O0","--coverage"])
    extra_link_args= ["--coverage"]

#Option to just compile the orbit extension
try:
    orbit_ext_pos = sys.argv.index('--orbit_ext')
except ValueError:
    orbit_ext= False
else:
    del sys.argv[orbit_ext_pos]
    orbit_ext= True

#Option to just compile the actionAngle extension
try:
    actionAngle_ext_pos = sys.argv.index('--actionAngle_ext')
except ValueError:
    actionAngle_ext= False
else:
    del sys.argv[actionAngle_ext_pos]
    actionAngle_ext= True

#Option to just compile the interppotential extension
try:
    interppotential_ext_pos = sys.argv.index('--interppotential_ext')
except ValueError:
    interppotential_ext= False
else:
    del sys.argv[interppotential_ext_pos]
    interppotential_ext= True

#code to check the GSL version
cmd= ['gsl-config',
      '--version']
try:
    if sys.version_info < (2,7): #subprocess.check_output does not exist
        gsl_version= subprocess.Popen(cmd,
                                      stdout=subprocess.PIPE).communicate()[0]
    else:
        gsl_version= subprocess.check_output(cmd)
except (OSError,subprocess.CalledProcessError):
    gsl_version= ['0','0']
else:
    gsl_version= gsl_version.split('.')
#HACK for testing
#gsl_version= ['0','0']

#Orbit integration C extension
orbit_int_c_src= ['galpy/util/bovy_symplecticode.c','galpy/util/bovy_rk.c']
orbit_int_c_src.extend(glob.glob('galpy/potential_src/potential_c_ext/*.c'))
orbit_int_c_src.extend(glob.glob('galpy/orbit_src/orbit_c_ext/*.c'))
orbit_int_c_src.extend(glob.glob('galpy/util/interp_2d/*.c'))

orbit_libraries=['m']
if float(gsl_version[0]) >= 1.:
    orbit_libraries.extend(['gsl','gslcblas'])
orbit_int_c= Extension('galpy_integrate_c',
                       sources=orbit_int_c_src,
                       libraries=orbit_libraries,
                       include_dirs=['galpy/util',
                                     'galpy/util/interp_2d',
                                     'galpy/potential_src/potential_c_ext'],
                       extra_compile_args=extra_compile_args,
                       extra_link_args=extra_link_args)
ext_modules=[]
if float(gsl_version[0]) >= 1. and \
        not actionAngle_ext and not interppotential_ext:
    orbit_int_c_incl= True
    ext_modules.append(orbit_int_c)
else:
    orbit_int_c_incl= False

#actionAngle C extension
actionAngle_c_src= glob.glob('galpy/actionAngle_src/actionAngle_c_ext/*.c')
actionAngle_c_src.extend(glob.glob('galpy/potential_src/potential_c_ext/*.c'))
actionAngle_c_src.extend(glob.glob('galpy/util/interp_2d/*.c'))

#Installation of this extension using the GSL may (silently) fail, if the GSL
#is built for the wrong architecture, on Mac you can install the GSL correctly
#using
#brew install gsl --universal
actionAngle_c= Extension('galpy_actionAngle_c',
                         sources=actionAngle_c_src,
                         libraries=pot_libraries,
                         include_dirs=['galpy/actionAngle_src/actionAngle_c_ext',
                                       'galpy/util/interp_2d',
                                       'galpy/potential_src/potential_c_ext'],
                         extra_compile_args=extra_compile_args,
                         extra_link_args=extra_link_args)
if float(gsl_version[0]) >= 1. and float(gsl_version[1]) >= 14. and \
        not orbit_ext and not interppotential_ext:
    actionAngle_c_incl= True
    ext_modules.append(actionAngle_c)
else:
    actionAngle_c_incl= False
    
#interppotential C extension
interppotential_c_src= glob.glob('galpy/potential_src/potential_c_ext/*.c')
interppotential_c_src.extend(glob.glob('galpy/potential_src/interppotential_c_ext/*.c'))
interppotential_c_src.extend(['galpy/util/bovy_symplecticode.c','galpy/util/bovy_rk.c'])
interppotential_c_src.append('galpy/actionAngle_src/actionAngle_c_ext/actionAngle.c')
interppotential_c_src.append('galpy/orbit_src/orbit_c_ext/integrateFullOrbit.c')
interppotential_c_src.extend(glob.glob('galpy/util/interp_2d/*.c'))

interppotential_c= Extension('galpy_interppotential_c',
                         sources=interppotential_c_src,
                         libraries=pot_libraries,
                         include_dirs=['galpy/potential_src/potential_c_ext',
                                       'galpy/util/interp_2d',
                                       'galpy/util/',
                                       'galpy/actionAngle_src/actionAngle_c_ext',
                                       'galpy/orbit_src/orbit_c_ext',
                                       'galpy/potential_src/interppotential_c_ext'],
                             extra_compile_args=extra_compile_args,
                             extra_link_args=extra_link_args)
if float(gsl_version[0]) >= 1. and float(gsl_version[1]) >= 14. \
        and not orbit_ext and not actionAngle_ext:
    interppotential_c_incl= True
    ext_modules.append(interppotential_c)
else:
    interppotential_c_incl= False

setup(name='galpy',
      version='0.2.alpha',
      description='Galactic Dynamics in python',
      author='Jo Bovy',
      author_email='bovy@ias.edu',
      license='New BSD',
      long_description=long_description,
      url='http://github.com/jobovy/galpy',
      package_dir = {'galpy/': ''},
      packages=['galpy','galpy/orbit_src','galpy/potential_src',
                'galpy/df_src','galpy/util','galpy/snapshot_src',
                'galpy/actionAngle_src'],
      package_data={'galpy/df_src':['data/*.sav'],
                    "": ["README.md","README.dev","LICENSE","AUTHORS.rst"]},
      include_package_data=True,
      install_requires=['numpy','scipy','matplotlib','nose'],
      ext_modules=ext_modules,
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: C",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics"]
      )

def print_gsl_message(num_messages=1):
    if num_messages > 1:
        this_str= 'these installations'
    else:
        this_str= 'this installation'
    print 'If you believe that %s should have worked, make sure\n(1) that the GSL include/ directory can be found by the compiler (you might have to edit CFLAGS for this: export CFLAGS="$CFLAGS -I/path/to/gsl/include/", or equivalent for C-type shells; replace /path/to/gsl/include/ with the actual path to the include directory),\n(2) that the GSL library can be found by the linker (you might have to edit LDFLAGS for this: export LDFLAGS="$LDFLAGS -L/path/to/gsl/lib/", or equivalent for C-type shells; replace /path/to/gsl/lib/ with the actual path to the lib directory),\n(3) and that `gsl-config --version` returns the correct version' % this_str

num_gsl_warn= 0
if not orbit_int_c_incl:
    num_gsl_warn+= 1
    print '\033[91;1m'+'WARNING: orbit-integration C library not installed because your GSL version < 1'+'\033[0m'

if not actionAngle_c_incl:
    num_gsl_warn+= 1
    print '\033[91;1m'+'WARNING: action-angle C library not installed because your GSL version < 1.14'+'\033[0m'
if not interppotential_c_incl:
    num_gsl_warn+= 1
    print '\033[91;1m'+'WARNING: Potential-interpolation C library not installed because your GSL version < 1.14'+'\033[0m'

if num_gsl_warn > 0:
    print_gsl_message(num_messages=num_gsl_warn)
    print '\033[1m'+'These warning messages about the C code do not mean that the python package was not installed successfully'+'\033[0m'
print '\033[1m'+'Finished installing galpy'+'\033[0m'
print 'You can run the test suite using `nosetests -v -w nose/` to check the installation (note that the test suite currently takes about 6 minutes to run)'
