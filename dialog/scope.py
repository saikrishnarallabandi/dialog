#!/usr/bin/env python3

"""
Scope manipulations.
"""
__author__ = "Mark Birger"
__date__ = "20 Nov 2014"

import sys
import multiprocessing

class Scope:
    """
    Class represents objects scope.
    Visible in dialog.
    """
    def __init__(self, scope):
        self.globals = scope
        self.scope = {}
        for name, obj in scope.items():
            if not name.startswith('__') and name != "Dialog":
                self.scope[name] = obj
        self.routines = {}

    def get(self, name):
        """
        Calls inline function or return variables.
        """
        try:
            if hasattr(self.scope[name], '__call__'):
                return self.scope[name]()
            else:
                return self.scope[name]
        except KeyError:
            print("ERROR:", name, "is not defined at the scope")
            sys.exit(1)

    def set(self, variables):
        """
        Set ups new variables from dictionary.
        """
        for key, value in variables.items():
            print("\t" + key, "<=", value)
        self.scope.update(variables)
        self.globals.update(variables)

    def parallel(self, name, return_queue):
        """
        Calls simplex routine, asynchroniously.
        """
        try:
            routine = multiprocessing.Process(
                target=self.scope[name],
                args=(return_queue, ))
        except KeyError:
            print("ERROR: simplex routine", name, "is not defined at the scope")
            sys.exit(1)
        routine.start()
        return routine

    def parallel2(self, name, requests_queue, return_queue):
        """
        Calls duplex routine, asynchroniously.
        """
        try:
            routine = multiprocessing.Process(
                target=self.scope[name],
                args=(requests_queue, return_queue, self.scope, ))
        except KeyError:
            print("ERROR: duplex routine", name, "is not defined at the scope")
            sys.exit(1)
        routine.start()
        self.routines[name] = {
            "process" : routine,
            "requests": requests_queue, 
        }
        return routine

    def send(self, name, value):
        """
        Send value to existing duplex routine.
        """
        to_delete = []
        if name in self.routines:
            if self.routines[name]["process"].is_alive():
                self.routines[name]["requests"].put(value)
            else:
                to_delete.append(name)
        else:
            pass
            #TODO: create error raising
        for each in to_delete:
            del self.routines[each]
