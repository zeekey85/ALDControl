#Main Program Loop Here. Don't forget to import the library.
import zakjeffALDLibrary as aldGO
import asyncio

while True:
    i = input("what would you like to do? (manualcontrol, runprogram, exit):  ")
    if i == "exit":
        print("goodbye")
        aldGO.setValve("whatever", "close")
        break
    elif i == "manualcontrol":
        print("you are now in manual conrol.")
        while True:
            manualinput = input("You can now call any function in the library (setMFC, setValve, setPP, setPS, getP). Type 'done' when done.")
            if manualinput == 'done':
                break
            elif manualinput == 'setMFC':
                fc=input("which flow controller do you want to set? Ar or N2")
                setpoint=int(input("what setpoint do you want?"))
                print(asyncio.run(aldGO.setMFC(fc, setpoint)))
            elif manualinput == 'setValve':
                aldGO.setValve(input('enter addr: '),int(input('enter state (1 = open): ')))
            elif manualinput == 'setPP':
                aldGO.setValve(input('enter addr: '),int(input('enter plasma power: ')))
            elif manualinput == 'setPS':
                aldGO.setValve(input('enter addr: '),input('enter plasma state (1 = on): '))
            elif manualinput == 'getP':
                print(aldGO.readPressure())
    elif i == "runprogram":
        file = aldGO.fileInput()
        loops = int(input("how many times you wanna run through this thing?"))
        print("here we go!")
        aldGO.aldRun(file,loops)
    else:
        print("Umm, what? Please try again.")
