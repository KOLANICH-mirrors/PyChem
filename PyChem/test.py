# a simple example of a class inheritance
# tested with Python24	   vegaseat	   10aug2005

help("object")  # test


class Class1(object):
	"""
	Class1 inherits the most basic container class object (just a place holder)
	this is the newer class writing convention, adding (object) is "still" optional
	"""

	k = 7

	def __init__(self, color="green"):
		"""
		Special method __init__() is called first (acts as Constructor).
		It brings in data from outside the class like the variable color.
		(in this case color is also set to a default value of green)
		The first parameter of any method/function in the class is always self,
		the name self is used by convention.  Assigning color to self.color allows it
		to be passed to all methods within the class.  Think of self as a carrier,
		or if you want impress folks call it target instance object.
		The variable k is assigned a value in the class, but outside of the methods.
		You can access k in a method using self.k
		"""
		self.color = color

	def Hello1(self):
		print("Hello from Class1!")

	def printColor(self):
		"""in this case self allows color to be passed"""
		print("I like the color", self.color)

	def __localHello(self):
		"""
		A variable or function with a double underline prefix and no or max. single
		underline postfix is considered private to the class and is not inherited or
		accessible outside the class.
		"""
		print("A hardy Hello only used within the class!")


class Class2(Class1):
	"""
	Class2 inherits Class1 (Class2 is the subclass, Class1 the base or superclass)
	Class1 has to be coded before Class2 for this to work!!!
	Class2 can now use any method of Class1, and even the variable k
	"""

	def Hello2(self):
		print("Hello from Class2!")
		print(self.k, "is my favorite number")


# the color blue is passed to __init__()
c1 = Class1("blue")

# Class2 inherited method __init__() from Class1
# if you used c2 = Class2(), the default color green would be picked
c2 = Class2("red")

print("-" * 20)
print("Class1 says hello:")
c1.Hello1()

print("-" * 20)
print("Class2 says a Class1 hello:")
c2.Hello1()

print("-" * 20)
print("Class2 says its own hello:")
c2.Hello2()

print("-" * 20)
print("Class1 color via __init__():")
c1.printColor()

print("-" * 20)
print("Class2 color via inherited __init__() and printColor():")
c2.printColor()

print("-" * 20)
print("Class1 changes its mind about the color:")
c1 = Class1("yellow")  # same as:  c1.__init__('yellow')
c1.printColor()

print("-" * 20)
print("Wonder what Class2 has to say now:")
c2.printColor()

print("-" * 20)
# this would give an error!	 Class1 does not have a method Hello2()
if hasattr(Class1, "Hello2"):
	print(c1.Hello2())
else:
	print("Class1 does not contain method Hello2()")

# check inheritance
if issubclass(Class2, Class1):
	print("Class2 is a subclass of Class1, or Class2 has inherited Class1")

# you can access variable k contained in Class1
print("Variable k from Class1 =", c1.k)

print("-" * 20)
# this would give an error!	 You cannot access a class private method
if hasattr(Class1, "__localHello()"):
	print(c1.__localHello())
else:
	print("No access to Class1 private method __localHello()")
