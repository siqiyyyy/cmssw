import os
import ROOT
import sys
from TkAlExceptions import AllInOneError

####################--- Helpers ---############################
def replaceByMap(target, the_map):
    """This function replaces `.oO[key]Oo.` by `the_map[key]` in target.

    Arguments:
    - `target`: String which contains symbolic tags of the form `.oO[key]Oo.`
    - `the_map`: Dictionary which has to contain the `key`s in `target` as keys
    """

    result = target
    for key in the_map:
        lifeSaver = 10e3
        iteration = 0
        while ".oO[" in result and "]Oo." in result:
            for key in the_map:
                try:
                    result = result.replace(".oO["+key+"]Oo.",the_map[key])
                except TypeError:   #try a dict
                    try:
                        for keykey, value in the_map[key].iteritems():
                           result = result.replace(".oO[" + key + "['" + keykey + "']]Oo.", value)
                           result = result.replace(".oO[" + key + '["' + keykey + '"]]Oo.', value)
                    except AttributeError:   #try a list
                        try:
                            for index, value in enumerate(the_map[key]):
                                result = result.replace(".oO[" + key + "[" + str(index) + "]]Oo.", value)
                        except TypeError:
                            raise TypeError("Something is wrong in replaceByMap!  Need a string, dict, or list, but the_map(%s)=%s!"%(repr(key), repr(the_map[key])))
                iteration += 1
            if iteration > lifeSaver:
                problematicLines = ""
                for line in result.splitlines():
                    if  ".oO[" in result and "]Oo." in line:
                        problematicLines += "%s\n"%line
                msg = ("Oh Dear, there seems to be an endless loop in "
                       "replaceByMap!!\n%s\n%s"%(problematicLines, the_map))
                raise AllInOneError(msg)
    return result


def getCommandOutput2(command):
    """This function executes `command` and returns it output.

    Arguments:
    - `command`: Shell command to be invoked by this function.
    """

    child = os.popen(command)
    data = child.read()
    err = child.close()
    if err:
        raise RuntimeError('%s failed w/ exit code %d' % (command, err))
    return data


def castorDirExists(path):
    """This function checks if the directory given by `path` exists.

    Arguments:
    - `path`: Path to castor directory
    """

    if path[-1] == "/":
        path = path[:-1]
    containingPath = os.path.join( *path.split("/")[:-1] )
    dirInQuestion = path.split("/")[-1]
    try:
        rawLines = getCommandOutput2("rfdir /"+containingPath).splitlines()
    except RuntimeError:
        return False
    for line in rawLines:
        if line.split()[0][0] == "d":
            if line.split()[8] == dirInQuestion:
                return True
    return False

def replacelast(string, old, new, count = 1):
    """Replace the last occurances of a string"""
    return new.join(string.rsplit(old,count))

fileExtensions = ["_cfg.py", ".sh", ".root"]

def addIndex(filename, njobs, index = None):
    if index is None:
        return [addIndex(filename, njobs, i) for i in range(njobs)]
    if njobs == 1:
        return filename

    fileExtension = None
    for extension in fileExtensions:
        if filename.endswith(extension):
            fileExtension = extension
    if fileExtension is None:
        raise AllInOneError(fileName + " does not end with any of the extensions "
                                     + str(fileExtensions))
    return replacelast(filename, fileExtension, "_" + str(index) + fileExtension)

def parsecolor(color):
    try: #simplest case: it's an int
        return int(color)
    except ValueError:
        pass

    try:   #kRed, kBlue, ...
        color = str(getattr(ROOT, color))
        return int(color)
    except (AttributeError, ValueError):
        pass

    if color.count("+") + color.count("-") == 1:  #kRed+5, kGreen-2
        if "+" in color:                          #don't want to deal with nonassociativity of -
            split = color.split("+")
            color1 = parsecolor(split[0])
            color2 = parsecolor(split[1])
            return color1 + color2

        if "-" in color:
            split = color.split("-")
            color1 = parsecolor(split[0])
            color2 = parsecolor(split[1])
            return color1 - color2

    raise AllInOneError("color has to be an integer, a ROOT constant (kRed, kBlue, ...), or a two-term sum or difference (kGreen-5)!")

def parsestyle(style):
    try: #simplest case: it's an int
        return int(style)
    except ValueError:
        pass

    try: #kStar, kDot, ...
        style = str(getattr(ROOT,style))
        return int(style)
    except (AttributeError, ValueError):
        pass

    raise AllInOneError("style has to be an integer or a ROOT constant (kDashed, kStar, ...)!")

def recursivesubclasses(cls):
    result = [cls]
    for subcls in cls.__subclasses__():
        result += recursivesubclasses(subcls)
    return result

def cache(function):
    cache = {}
    def newfunction(*args, **kwargs):
        try:
            return cache[args, tuple(sorted(kwargs.iteritems()))]
        except TypeError:
            print args, tuple(sorted(kwargs.iteritems()))
            raise
        except KeyError:
            cache[args, tuple(sorted(kwargs.iteritems()))] = function(*args, **kwargs)
            return newfunction(*args, **kwargs)
    newfunction.__name__ = function.__name__
    return newfunction

def boolfromstring(string, name):
    """
    Takes a string from the configuration file
    and makes it into a bool
    """
    #try as a string, not case sensitive
    if string.lower() == "true": return True
    if string.lower() == "false": return False
    #try as a number
    try:
        return str(bool(int(string)))
    except ValueError:
        pass
    #out of options
    raise ValueError("{} has to be true or false!".format(name))
    

def pythonboolstring(string, name):
    """
    Takes a string from the configuration file
    and makes it into a bool string for a python template
    """
    return str(boolfromstring(string, name))

def cppboolstring(string, name):
    """
    Takes a string from the configuration file
    and makes it into a bool string for a C++ template
    """
    return pythonboolstring(string, name).lower()

def conddb(*args):
    """
    Wrapper for conddb, so that you can run
    conddb("--db", "myfile.db", "listTags"),
    like from the command line, without explicitly
    dealing with all the functions in CondCore/Utilities.
    getcommandoutput2(conddb ...) doesn't work, it imports
    the wrong sqlalchemy in CondCore/Utilities/python/conddblib.py
    """
    from tempfile import NamedTemporaryFile

    with open(getCommandOutput2("which conddb").strip()) as f:
        conddb = f.read()

    def sysexit(number):
        if number != 0:
            raise AllInOneError("conddb exited with status {}".format(number))
    namespace = {"sysexit": sysexit, "conddboutput": ""}

    conddb = conddb.replace("sys.exit", "sysexit")

    bkpargv = sys.argv
    sys.argv[1:] = args
    bkpstdout = sys.stdout
    with NamedTemporaryFile(bufsize=0) as sys.stdout:
        exec conddb in namespace
        namespace["main"]()
        with open(sys.stdout.name) as f:
            result = f.read()

    sys.argv[:] = bkpargv
    sys.stdout = bkpstdout

    return result
