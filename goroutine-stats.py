import os, sys

usage = " \
*** Usage: *** \n \
Get an idea of what goroutines were doing when go dumped them. \n \
For example, which goroutines were created by what code, and how \n \
many there were of each at the time of the dump. \n \
        "
def main():
    if len(sys.argv) != 2 :
        print usage
        return
    outfile = sys.argv[1]
    if not os.stat(outfile):
        print("no permission to path %s" % outfile)
        return

    results = do_work(outfile)
    print('')
    for x in results:
        total = 0
        for (k,v) in results[x].items():
            total += v
        print("%s (%d): " %(x,total))
        for (k,v) in results[x].items():
            print ("\t %s: %d" %(k,v))


def do_work(outfile):
    # first find a goroutine (e.g. "goroutine 3706 [syscall, 123 minutes]:") line, and
    # parse out the function it's in (e.g. syscall), which will be after the only '['.
    # Add that to a dict of dicts, where each dict key is a the function, and each item
    # in the list is the code that created the goroutine, and a count of how many times
    # that code created a goroutine that was in a particular function at dump time.
    # then find the line after it that has 'created by,' (and it won't be counted if we
    # find another goroutine line first) and, if it isn't in the dict, add it, along with
    # the code and '1.'
    # If it is in the list, up the count in the dict matching the code path string.
    # e.g. {"syscall": {"blah_path", x, "blah_path2": x}}
    # All this should keep the size small and have O(N) time.

    results = dict()
    with open(outfile, 'r') as f:
        func_name = ''
        for line in f.readlines():
            # throw away everything before the last ':' (date, etc.)
            cut_line = [x.strip() for x in line.strip().split(':')[3:] if x is not ''][0]
            if "goroutine" in cut_line:
                in_brackets = cut_line[cut_line.find('[')+1:cut_line.find(']')]
                func_name = in_brackets.split(',')
                if len(func_name) is 1:
                    continue
                func_name = func_name[0]
            elif "created" in cut_line:
                if len(func_name) is 1:
                    continue
                code_path = cut_line.split()[2]
                try:
                    creators = results[func_name] # another dict
                    try:
                        creator_count = creators[code_path]
                        results[func_name][code_path] = creator_count + 1
                    except KeyError:
                        results[func_name][code_path] = 1
                except KeyError:
                    results[func_name] = {}

    return results

if __name__ == "__main__":
        main()
