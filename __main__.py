

import pulumi
from virtualmachine  import vm,vmArgs


vmach1 = vm("vmach1",vmArgs(username="admin123",password="Unif!12#"))


vmach2 = vm("vmach2",vmArgs(username="admin1234",password="Unif!12#4"))




