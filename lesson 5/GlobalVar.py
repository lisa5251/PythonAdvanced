x = 10

def my_function():
    global x
    x = 20  # modifies the global variable

my_function()
print(x)  # prints 20

def test():
    name = "Lisa"
    print(name)

test()