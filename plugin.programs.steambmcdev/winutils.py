"""
Windows utils for launching programs, managing processes, etc.
Copyright (C) 2013 T. Oldbury

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.
"""

import subprocess

"""
shellOutput: Execute a shell command, return the output.

@param      Command to execute

@return     Result of command, as a string
"""
def shellOutput(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    lines = []
    while True:
        ret = p.poll() 
        line = p.stdout.readline()
        lines.append(line)
        if ret == 0:
            break
    return "\n".join(lines)

"""
getProcessesList: Get the list of running processes.

@return     List of running executables
"""
def getProcessesList():
    tasklist = shellOutput("tasklist")
    tasks = []
    for line in tasklist.split('\n')[5:]:
        parts = line.split('  ') # re.split?
        if len(parts) > 1:
            if parts[0].startswith("System Idle Process") or parts[0].strip() == "System":
                continue
            tasks.append(parts[0].strip())
    return tasks


"""
launchFork: Launch an application (forked execution.) Return immediately. 
            Simply a subprocess wrapper. (For now...)
"""
def launchFork(cmd):
    subprocess.Popen(cmd, shell=True)

