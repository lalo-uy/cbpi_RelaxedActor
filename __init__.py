''' 


'''
import time
from modules import cbpi
from modules.core.props import Property
from modules.core.hardware import ActorBase

relaxed_actor_ids = []

@cbpi.actor
class RelaxedActor(ActorBase):

    a_actor= Property.Actor("Slave Actor", description= "Actor to be driven by this one")
    on_max = Property.Number("On max", True, 55, description="Max on time min")
    off_pause = Property.Number("Off pause", True , 5, description="Pause time min")

    def init(self):
        self.onTimer = 0
        self.pauseTimer = 0
        if isinstance(self.a_actor, unicode) and self.a_actor:
            self.slave_actor = (int(self.a_actor))
        else:
            self.slave_actor = None
      
        if not int(self.id) in relaxed_actor_ids:
            relaxed_actor_ids.append(int(self.id))      
  


    def execute_func(self):
      if (self.slave_actor is not None):
         if ( self.onTimer > 0 ) and (self.onTimer < time.time() ) :
            self.onTimer = 0;
            self.pauseTimer = time.time() + float(self.off_pause)*60
            print "Slave paused"
            self.api.switch_actor_off(self.slave_actor)
           
         if ( self.pauseTimer > 0 ) and (self.pauseTimer < time.time() ) :
            self.pauseTimer = 0;
            self.onTimer = time.time() + float(self.on_max)*60
            print "Slave on"
            self.api.switch_actor_on(self.slave_actor)
           


    def set_power(self, power):
        if self.slave_actor is not None:
            self.api.actor_power(self.slave_actor, power=power)

    def on(self, power=None):
        print "Slave on"
        self.api.switch_actor_on(self.slave_actor)
        self.onTimer = time.time() + float(self.on_max)*60

    def off(self):
        print "Slave off"
        self.api.switch_actor_off(self.slave_actor)
        self.onTimer = 0
        self.pauseTimer = 0
        
@cbpi.backgroundtask(key="actor_execute", interval=1)
def actor_execute(api):
    global relaxed_actor_ids
    for id in relaxed_actor_ids:
        actor = cbpi.cache.get("actors").get(id)
        #test for deleted Func actor
        if actor is None:
            relaxed_actor_ids.remove(id)
        else:
            try:    # try to call execute. Remove if execute fails. Added back when settings updated
                actor.instance.execute_func()
            except Exception as e:
                print e
                cbpi.notify("Actor Error", "Failed to execute actor %s. Please update the configuraiton" % actor.name, type="danger", timeout=0)
                cbpi.app.logger.error("Execute of Actor %s failed, removed from execute list" % id)  
                relaxed_actor_ids.remove(id)   
      
