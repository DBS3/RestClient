import sys, os, os.path, re, shutil, string
from distutils.core import setup, Command
from distutils.command.build import build
from distutils.command.install import install
from distutils.spawn import spawn
from glob import glob

systems = \
{
  'RestClient':
  {
    'srcdir': 'src/python',
    'pythonmods': ['RestClient.__init__',
                   'RestClient.RestApi'],
    'pythonpkg': ['RestClient.AuthHandling',
                  'RestClient.ErrorHandling',
                  'RestClient.ProxyPlugins',
                  'RestClient.RequestHandling']
  }
}

def get_relative_path():
  return os.path.dirname(os.path.abspath(os.path.join(os.getcwd(), sys.argv[0])))

def define_the_build(self, dist, system_name, run_make = True, patch_x = ''):
  # Expand various sources.
  docroot = "doc/build/html"
  system = systems[system_name]
  confsrc = sum((glob("conf/%s" % x) for x in system.get('conf',[])), [])
  binsrc = sum((glob("%s" % x) for x in system.get('bin', [])), [])

  # Specify what to install.
  py_version = (string.split(sys.version))[0]
  pylibdir = '%slib/python%s/site-packages' % (patch_x, py_version[0:3])
  dist.py_modules = system.get('pythonmods', [])
  dist.packages = system.get('pythonpkg', [])
  dist.package_dir = { '': system.get('srcdir', []) }
  dist.data_files = [('%sbin' % patch_x, binsrc), ('conf', confsrc)]
  if os.path.exists(docroot):
    for dirpath, dirs, files in os.walk(docroot):
      dist.data_files.append(("%sdoc%s" % (patch_x, dirpath[len(docroot):]),
                              ["%s/%s" % (dirpath, fname) for fname in files
                               if fname != '.buildinfo']))

class BuildCommand(Command):
  """Build python modules for a specific system."""
  description = \
    "Build python modules for the specified system. Possible\n" + \
    "\t\t   systems are 'RestClient'.\n" + \
    "Use with --force to\n" + \
    "\t\t   ensure a clean build of only the requested parts.\n"
  user_options = build.user_options
  user_options.append(('system=', 's', 'build the specified system'))

  def initialize_options(self):
    self.system = 'RestClient'

  def finalize_options(self):
    # Check options.
    if self.system == None:
      print "System not specified, please use '-s RestClient'"
      sys.exit(1)
    elif self.system not in systems:
      print "System %s unrecognised, please use '-s RestClient'" % self.system
      sys.exit(1)

    # Expand various sources and maybe do the c++ build.
    define_the_build(self, self.distribution, self.system, True, '')

    # Force rebuild.
    shutil.rmtree("%s/build" % get_relative_path(), True)
    shutil.rmtree("doc/build", True)

  def generate_docs(self):
    os.environ["PYTHONPATH"] = "%s/build/lib:%s" % (os.getcwd(), os.environ["PYTHONPATH"])
    spawn(['make', '-C', 'doc', 'html', 'PROJECT=RestClient'])

  def run(self):
    command = 'build'
    if self.distribution.have_run.get(command): return
    cmd = self.distribution.get_command_obj(command)
    cmd.force = self.force
    cmd.ensure_finalized()
    cmd.run()
    self.generate_docs()
    self.distribution.have_run[command] = 1

class InstallCommand(install):
  """Install a specific system."""
  description = \
    "Install a specific system, 'RestClient'. You can\n" + \
    "\t\t   patch an existing installation instead of normal full installation\n" + \
    "\t\t   using the '-p' option.\n"
  user_options = install.user_options
  user_options.append(('system=', 's', 'install the specified system'))
  user_options.append(('patch', None, 'patch an existing installation'))

  def initialize_options(self):
    install.initialize_options(self)
    self.system = 'RestClient'
    self.patch = None

  def finalize_options(self):
    # Check options.
    if self.system == None:
      print "System not specified, please use '-s RestClient'"
      sys.exit(1)
    elif self.system not in systems:
      print "System %s unrecognised, please use '-s RestClient'" % self.system
      sys.exit(1)
    if self.patch and not os.path.isdir("%s/xbin" % self.prefix):
      print "Patch destination %s does not look like a valid location." % self.prefix
      sys.exit(1)

    # Expand various sources, but don't build anything from c++ now.
    define_the_build(self, self.distribution, self.system,
                     False, (self.patch and 'x') or '')

    # Whack the metadata name.
    self.distribution.metadata.name = self.system
    assert self.distribution.get_name() == self.system

    # Pass to base class.
    install.finalize_options(self)

    # Mangle paths if we are patching. Most of the mangling occurs
    # already in define_the_build(), but we need to fix up others.
    if self.patch:
      self.install_lib = re.sub(r'(.*)/lib/python(.*)', r'\1/xlib/python\2', self.install_lib)
      self.install_scripts = re.sub(r'(.*)/bin$', r'\1/xbin', self.install_scripts)

  def run(self):
    for cmd_name in self.get_sub_commands():
      cmd = self.distribution.get_command_obj(cmd_name)
      cmd.distribution = self.distribution
      if cmd_name == 'install_data':
        cmd.install_dir = self.prefix
      else:
        cmd.install_dir = self.install_lib
      cmd.ensure_finalized()

      self.run_command(cmd_name)
      self.distribution.have_run[cmd_name] = 1

#By default setuptools calls python setup.py build for dependencies. If another package depends on RestClient,
# setuptools will fail to install RestClient. So rewrite build and install parameter to build_system and install_system
for index, option in enumerate(sys.argv):
    if option in ('build', 'install'):
        sys.argv[index] += '_system'


setup(name = 'RestClient',
      version = '0.1',
      maintainer_email = 'hn-cms-dmDevelopment@cern.ch',
      cmdclass = { 'build_system': BuildCommand,
                   'install_system': InstallCommand })
