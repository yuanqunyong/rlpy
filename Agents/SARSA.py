######################################################
# Developed by Alborz Geramiard Oct 25th 2012 at MIT #
######################################################
from Agent import *
class SARSA(Agent):
    lambda_ = 0        #lambda Parameter in SARSA [Sutton Book 1998]
    eligibility_trace   = []
    eligibility_trace_s = [] # eligibility trace using state only (no copy-paste), necessary for dabney decay mode
    def __init__(self, representation, policy, domain,logger, initial_alpha =.1, lambda_ = 0, alpha_decay_mode = 'dabney', boyan_N0 = 1000):
        self.eligibility_trace  = zeros(representation.features_num*domain.actions_num)
        self.eligibility_trace_s= zeros(representation.features_num) # use a state-only version of eligibility trace for dabney decay mode
        self.lambda_            = lambda_
        super(SARSA,self).__init__(representation,policy,domain,logger,initial_alpha,alpha_decay_mode, boyan_N0)
        self.logger.log("Alpha_0:\t\t%0.2f" % initial_alpha)
        self.logger.log("Decay mode:\t\t"+str(alpha_decay_mode))
        
        if lambda_: self.logger.log("lambda:\t%0.2f" % lambda_)
    def learn(self,s,a,r,ns,na,terminal):
        super(SARSA, self).learn(s,a,r,ns,na,terminal) # increment episode count
        gamma               = self.representation.domain.gamma
        theta               = self.representation.theta
        phi_s               = self.representation.phi(s)
        phi_prime_s         = self.representation.phi(ns)
        phi                 = self.representation.phi_sa(s,a,phi_s)
        phi_prime           = self.representation.phi_sa(ns,na,phi_prime_s)
        
        print 's,ns',s,ns
        print 'phi_nnz, phi_prime_nnz',count_nonzero(phi),count_nonzero(phi_prime)
		
        nnz                 = count_nonzero(phi_s)    #Number of non-zero elements
        if nnz > 0: # Phi has some nonzero elements, proceed with update
            #Set eligibility traces:
            if self.lambda_:
                self.eligibility_trace   *= gamma*self.lambda_
                self.eligibility_trace   += phi
                
                self.eligibility_trace_s  *= gamma*self.lambda_
                self.eligibility_trace_s += phi_s
                
                #Set max to 1
                self.eligibility_trace[self.eligibility_trace>1] = 1
                self.eligibility_trace_s[self.eligibility_trace_s>1] = 1
            else:
                self.eligibility_trace    = phi
                self.eligibility_trace_s  = phi_s
            
            td_error            = r + dot(gamma*phi_prime - phi, theta)
            
            print 'nonzeroelems,ind in phi', [(ind,elem) for ind,elem in enumerate(phi) if elem != 0]
            print 'nonzeroelems,ind in phi_prime', [(ind,elem) for ind,elem in enumerate(phi_prime) if elem != 0]
            print 'nonzeroelems,ind in elig', [(ind,elem) for ind,elem in enumerate(gamma*phi_prime-phi) if elem != 0]
            self.updateAlpha(phi_s,phi_prime_s,gamma,terminal)
            #theta               += self.alpha * td_error * self.eligibility_trace
            #print candid_alpha
			
            #use this if you want to divide by the number of active features  [[do this for PST]]
            theta               += self.alpha * td_error * phi / (1.*nnz) 

            print 'alpha',self.alpha
			
            #Discover features using online iFDD
            if isinstance(self.representation,iFDD):
                self.representation.discover(phi_s,td_error)
			
            # Set eligibility Traces to zero if it is end of the episode
            if self.lambda_: self.eligibility_trace = zeros(self.representation.features_num*self.domain.actions_num) 
            # Else there are no nonzero elements, halt update.
