#!/usr/bin/python
import os, sys, zlib
class CommitNode:
    def __init__(self, commit_hash):
        """
        :type commit_hash: str
        """
        self.commit_hash = commit_hash
        self.parents = set()
        self.children = set()

def get_branches(path, branch):
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(path):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.
            f = open(filepath, "r")
            c = f.read().rstrip('\n')
            # if the commit is already in the dict, simply add
            if c in branch:
                branch[c].add(filepath.removeprefix(path+'/'))
            # otherwise create new dict entry
            else:
                branch[c] = {filepath.removeprefix(path+'/')}
    return file_paths  # Self-explanatory.

def extract(obj_path, hash):  # decoding git object and placing each word into array
        filename = obj_path+'/'+hash[:2]+'/'+hash[2:]
        c_f = open(filename, 'rb')
        d_f = zlib.decompress(c_f.read()).decode()
        content = d_f.split()
        return content

# est relationships between commits and their parents and adding to dict and root
def process_parent(parent, obj_path, root, nodes, to_process):
    content = extract(obj_path, parent.commit_hash)
    i = 0
    while i < len(content) - 1:
        if content[i] == 'parent':
            par = CommitNode(content[i+1])
            if par.commit_hash in nodes:
                nodes[par.commit_hash].children.add(parent.commit_hash)
                parent.parents.add(par.commit_hash)
            else:
                par.children.add(parent.commit_hash)
                parent.parents.add(par.commit_hash)
                exists = False
                for x in to_process:
                    if x.commit_hash == par.commit_hash:
                        x.children.add(parent.commit_hash)
                        exists = True
                if exists == False:
                    to_process.append(par)
        i += 1
    if len(parent.parents) == 0:
        root.add(parent.commit_hash)
    # add commit to dict of all nodes
    # if that commit was already in nodes, update cur and pop old commit
    if parent.commit_hash in nodes:
        nodes[parent.commit_hash].parents.update(parent.parents)
        nodes[parent.commit_hash].children.update(parent.children)
    else:
        nodes[parent.commit_hash] = parent

def process_branches(obj_path, branches, root, nodes, to_process):
    for hash in branches:   # adding commits in branches into node dict
        cur = CommitNode(hash)
        content = extract(obj_path, hash)
        i = 0
        # adding its parents
        while i < len(content) - 1:
            if content[i] == 'parent':
                par = CommitNode(content[i+1])
                if par.commit_hash in nodes:
                    nodes[par.commit_hash].children.add(cur.commit_hash)
                    cur.parents.add(par.commit_hash)
                else:
                    par.children.add(cur.commit_hash)
                    cur.parents.add(par.commit_hash)
                    exists = False
                    for x in to_process:
                        if x.commit_hash == par.commit_hash:
                            x.children.add(cur.commit_hash)
                            exists = True
                    if exists == False:
                        to_process.append(par)
                    # process_parent(par, obj_path, root, nodes)
            i += 1
        # if no parents, add to root_commits
        if len(cur.parents) == 0:
            root.add(cur.commit_hash)
        # add commit to dict of all nodes
        # if that commit was already in nodes, update cur and pop old commit
        if cur.commit_hash in nodes:
            nodes[cur.commit_hash].parents.update(cur.parents)
            nodes[cur.commit_hash].children.update(cur.children)
        else:
            nodes[cur.commit_hash] = cur

def copy_nodes(nodes):
    # makes a deep copy of the nodes
    copy = {}
    for k, v in nodes.items():
        cur = CommitNode(k)
        for p in v.parents:
            cur.parents.add(p)
        for c in v.children:
            cur.children.add(c)
        copy[k] = cur
    return copy

def topo_sort(roots, nodes):
    result = [] # hold final result
    nodes_copy = copy_nodes(nodes)  # create copy of dict
    need_process = []
    for r in roots:
        need_process.append(r)

    while len(need_process) > 0:
        node = need_process.pop(0)
        commit = nodes_copy[node]    # gets node with no parents
        result.append(nodes[node])   # add to sorted array
        # update the children to remove the parent
        for next in commit.children:
            child = nodes_copy[next]
            child.parents.remove(node)
            # if it has no more children, add it to set of nodes to evaluate
            if len(child.parents) == 0:
                need_process.append(child.commit_hash)
    if len(result) < len(nodes):
        raise Exception("cycle detected")
    return result

def main():
    dir_name = ".git" # target directory
    cur_dir = os.getcwd() # current directory we are in
    git_dir = '' # where .git is

    while True:
        file_list = os.listdir(cur_dir) # list of all files and dirs in cur_dir
        parent_dir = os.path.dirname(cur_dir) # parent of current directory
        if dir_name in file_list: # traverse all files/dirs to see if theres a .git
            git_dir = cur_dir+'/'+dir_name
            break
        else:
            if cur_dir == parent_dir: #if dir is root dir
                print ("Not inside a Git repository")
                break
            else:
                cur_dir = parent_dir    # moves up a directory
    object_dir = git_dir+'/objects'
    branch = {} # dict to hold branch names and hashes
    branch_names = get_branches(git_dir+'/refs/heads', branch)  # gets names of the branches in .git/refs/heads
    root_commits = set()   # initialize set of commit hashes without parents
    nodes = {}  # dict to hold all nodes so we dont have to search every time
    to_process = []
    process_branches(object_dir, branch, root_commits, nodes, to_process) # creating nodes out of commits
    while len(to_process) > 0:  # while there are still nodes to process
        for p in to_process:
            process_parent(p, object_dir, root_commits, nodes, to_process)
            to_process.remove(p)
    topo_sorted = []
    topo_sorted = topo_sort(root_commits, nodes)    # topologically sorted commits
    topo_sorted.reverse()   # its in the wrong order so we need to reverse it
    i = 0
    sticky = False
    sticky_end = ''
    sticky_start = '='
    while i < len(topo_sorted) - 1: # print all but the last commit in list
        if sticky:  # if we need a stick start
            sticky = False  # reset stick to false
            sticky_start += ' '.join(topo_sorted[i].children)   # add all the children to the sticky_start string
            print(sticky_start)
            sticky_start = '='
        b = ''
        if topo_sorted[i].commit_hash in branch:    # if it corresponds to a branch head
            lex_sort = sorted(branch[topo_sorted[i].commit_hash])   # sort the branch names
            for name in lex_sort:
                b = b + ' ' + name
        print(topo_sorted[i].commit_hash+b)
        if not topo_sorted[i+1].commit_hash in topo_sorted[i].parents:  # if the next commit to be printed is not a parent
            sticky_end = ' '.join(topo_sorted[i].parents) + '=\n'   # add its parents to the sticky_end string
            print(sticky_end)
            sticky=True
            sticky_end=''
        i+=1
    # the remaining code takes care of the last commit in array
    if sticky:
        sticky_start += ' '.join(topo_sorted[len(topo_sorted) - 1].children)
        print(sticky_start)
    b = ''
    if topo_sorted[i].commit_hash in branch:
        lex_sort = sorted(branch[topo_sorted[i].commit_hash])
        for name in lex_sort:
            b = b + ' ' + name
    print(topo_sorted[i].commit_hash+b)
    
# I ran 'strace -o /u/cs/ugrad/hannac/trace.txt pytest' in the command line, and examined the trace.txt file

if __name__ == "__main__":
    main()