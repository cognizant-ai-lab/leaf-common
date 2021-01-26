DEF sez:

Not especially happy with this layer as it cements a 1:1 relationship
with SerializationFormats too soon in the hierarchy.  Eventually would
like to see fewer classes here that feed into a single more consolidated 
abstractation that can handle multiple SerializationFormats and
PeristenceMechanisms without the class being abstract.  Easy classes would
still ride on top of this as a client.
