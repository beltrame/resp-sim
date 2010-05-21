"""This module contains the fault injection manager. Its tasks are to generate and execute fault simulations"""
                       
class faultInjector:
    """ This class support the definition and execution a fault injection campaign """
    def __init__(self, locationDistribution, timeDistribution):
        """Constructor"""
        #set to empty list the locations and the current fault list. 
        #The location is a list of location descriptors used for generating the fault list
        self.__currentFaultList = []
        self.__locationDistribution = locationDistribution
        self.__timeDistribution = timeDistribution
           
    def generateFaultList(self, simulationDuration, numberOfSims, numberOfTimeIntervals =1):
        """Generates a fault injection list"""
        if not (isinstance(simulationDuration,int) or isinstance(simulationDuration,long)):
            raise exceptions.Exception("simulationDuration must be a number")
        if not (simulationDuration > 0):
            raise exceptions.Exception("simulationDuration must be a positive number")
        if not (isinstance(numberOfSims,int) or isinstance(numberOfSims,long)):
            raise exceptions.Exception("numberOfSims must be a number")
        if not (numberOfSims > 0):
            raise exceptions.Exception("numberOfSims must be a positive number")
        if not (isinstance(numberOfTimeIntervals,int) or isinstance(numberOfTimeIntervals,long)):
            raise exceptions.Exception("numberOfTimeIntervals must be a number")
        if not (numberOfTimeIntervals > 0):
            raise exceptions.Exception("numberOfTimeIntervals must be a positive number")

        #reset current fault list
        self.__currentFaultList = []
        self.__timeDistribution.setSimulationDuration(simulationDuration)
        self.__timeDistribution.setNumberOfTimeIntervals(numberOfTimeIntervals)
        #generate numberOfSims simulations
        for s in range(0,numberOfSims):
            #get time instants
            times = self.__timeDistribution()
            currSim = {}
            t = -1
            for t in range(0,len(times)-1):
                curr_t = times[t]
                curr_l = self.__locationDistribution()
                currSim[curr_t] = curr_l
            #insert a dummy entry for executing the last time interval
            currSim[times[t+1]] = {}
            self.__currentFaultList.append(currSim)
     
    def printFaultList(self):
        """Prints on the screen the current fault list """
        for s in range(0,len(self.__currentFaultList)):
            print 'Simulation #' + str(s)
            times = self.__currentFaultList[s].keys()
            times.sort()
            for t in times:
                print '\t' + str(t) 
                for f in self.__currentFaultList[s][t]:
                    for i in f.keys():
                        print '\t\t' + str(i) + '\t' + str(f[i])       
            
    def saveFaultList(self, filename):
        """"Saves in a file the current fault list"""
        import server
        fp=open(filename,'w')
        fp.write(server.encode_compound(self.__currentFaultList))
        fp.close()
        
    def loadFaultList(self, filename):
        """Loads a fault list from a file"""
        import server
        fp=open(filename,'r')
        filecontent = ''
        self.__currentFaultList = []
        for l in fp:
            filecontent = filecontent + l
        fp.close()
        self.__currentFaultList = server.decode_compound(filecontent)        
     
    def printFaultList(self):
        """Prints on the screen the current fault list """
        for s in range(0,len(self.__currentFaultList)):
            print 'Simulation #' + str(s)
            times = self.__currentFaultList[s].keys()
            times.sort()
            for t in times:
                print '\t' + str(t) 
                for f in self.__currentFaultList[s][t]:
                    for i in f.keys():
                        print '\t\t' + str(i) + '\t' + str(f[i])       
            
    def saveFaultList(self, filename):
        """"Saves in a file the current fault list"""
        import server
        fp=open(filename,'w')
        fp.write(server.encode_compound(self.__currentFaultList))
        fp.close()
            
    def loadFaultList(self, filename):
        """Loads a fault list from a file"""
        import server
        fp=open(filename,'r')
        filecontent = ''
        self.__currentFaultList = []
        for l in fp:
            filecontent = filecontent + l
        fp.close()
        self.__currentFaultList = server.decode_compound(filecontent)        
    
    def executeCampaign(self):
        """Executes a fault injection campaign with the current fault list"""

        #save fault list. It will be loaded by the server...
        self.saveFaultList('__temp_list')
        
        #import necessary modules     
        from hci import server_api
        from server_api import RespClient 
        import os
        import server
        import subprocess
        import sys
        import respkernel
        import resp
                            
        #set-up control stuff
        server_on = False #is the server on or not?
        rc = None #resp client reference
        subproc = None #server subprocess reference
        num_of_errors = 0 #number of server instances that has crashed

        #execute the fault campaign        
        try:
            for sim in range(0,len(self.__currentFaultList)):
                print "-------------------------------------------------------------------------------------------------------" 
                print "Simulation # " + str(sim)
                #start server if it not on
                if not server_on:
                    archFile = os.path.abspath(respkernel.get_architecture_filename())
                    respFile = os.path.abspath(sys.modules['resp'].__file__)
                    subproc = subprocess.Popen( ['python', respFile, '-s', '2200', '-a', archFile, '--silent', '--no-banner'], stdin=subprocess.PIPE, stdout=sys.stdout )
                    server_on = True
                    ok = False
                    rc = None
                    while not ok:
                        try:
                            rc = RespClient( 'localhost', 2200 )
                            ok = True
                        except:
                            pass
                    rc.execute('fim = manager.getFaultInjector()')
                    rc.execute('fim.loadFaultList(\'__temp_list\')')
                rc.execute('fim.executeSingleFault(' + str(sim) +')')
                error = server.decode_compound(rc.execute('controller.error'))
                #stop server when necessary
                if error == True or sim == (len(self.__currentFaultList)-1):
                    if error == True:
                        num_of_errors = num_of_errors +1
                    if sim == (len(self.__currentFaultList)-1):
                        os.remove('__temp_list')
                    rc.send('QUIT')
                    server_on = False
                    subproc.wait()
                else:
                    rc.execute('reset()')
                    rc.execute('reload_architecture()')  
        except Exception, e:
            import traceback
            traceback.print_exc()

            os.remove('__temp_list')
            if not (subproc == None):    
                import signal
                os.kill(subproc.pid, signal.SIGKILL)
            raise e
        
        try:
            # Call a custom statsprinter if registered
            resp_ns['campaignReportPrinter']()  #TODO FIX-IT!
        except:
            print "\n\n-------------------------------------------------------------------------------------------------------" 
            print "Statistics:"
            print "Number of simulations: " + str(len(self.__currentFaultList))
            print "Number of simulation terminated with an error: " + str(num_of_errors)
            print "-------------------------------------------------------------------------------------------------------" 

    def executeSingleFault(self, num):
        """Executes a fault simulation"""
        import respkernel
        resp_ns = respkernel.get_namespace()
        controller = resp_ns['controller']

        #import of required modules
        import attributeWrapper

        if controller.interactive == True:
            raise exceptions.Exception('It is not possible to run executeSingleFault function in the interactive mode')
        
        if not isinstance(num,int) and not isinstance(num,long):
            raise exceptions.Exception('Not compatible parameter received by the executeSingleFault function')
        if not num >= 0 and num < self.__currentFaultList:
            raise exceptions.Exception('Not compatible parameter received by the executeSingleFault function')            
        command = self.__currentFaultList[num]
        
        times = command.keys()
        if not (len(times) > 0):
            raise exceptions.Exception('Empty fault list: the simulation cannot be executed')
        
        #compute time deltas to be run
        times.sort()
        delta = {}
        delta[times[0]] = times[0]
        for i in range(1,len(times)):
            delta[times[i]] = times[i] - times[i-1]
        print times
        for t in times: #execute all delta and inject
            #run for a delta time            
            controller.run_simulation(delta[t])                        
            print controller.get_simulated_time()
            
            #inject fault
            if not t == times[len(times)-1]: #after the last delta time no injection is performed
                injections = command[t]
                #inject all the faults
                for fault in injections:
                    #get the reference to the class of the mask function
                    maskFunctionName = fault['mask_function']
                    if dir(resp_ns).count(maskFunctionName) != 0:
                        maskFunction = resp_ns[maskFunctionName]()
                    elif dir(attributeWrapper).count(maskFunctionName) != 0:#maskFunctions.count(maskFunctionName) != 0:
                        maskFunction = getattr(attributeWrapper,maskFunctionName)()
                    else:
                        raise exceptions.Exception( str(maskFunctionName) + ' is not a valid mask function')
                    
                    #get the reference to the class of the attribute wrapper
                    wrapperClassName = fault['wrapper']
                    if dir(resp_ns).count(wrapperClassName) != 0:
                        wrapperClass = resp_ns[wrapperClassName]
                    elif dir(attributeWrapper).count(wrapperClassName) != 0:
                        wrapperClass = getattr(attributeWrapper,wrapperClassName)
                    else:
                        raise exceptions.Exception( str(wrapperClassName) + ' is not a valid wrapper class')
                    
                    wrapper = wrapperClass(resp_ns['manager'].getCompInstance(fault['component']), fault['attribute'], maskFunction, fault['line'])
                    wrapper.applyMask(fault['mask'])                    

            #check if simulation is finished
            if controller.is_finished() or controller.error == True: 
                break
        if not controller.is_finished():
            controller.stop_simulation()
            
    