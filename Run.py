from FET_Calculator import Calculator as Calculator
import pandas as pd
import os

# add semiconductor type
# add the calculation for each circle


def run(datapath, widthpath, outputpath, period, skiprow, thickness):

    #path = 'c:\\Users\\GSJ\\Desktop\\d1\\f4\\data'
    # widthpath='C:\\Users\\GSJ\\Desktop\\d1\\f4\\channel.csv'
    datapath = datapath
    widthpath = widthpath
    outputpath = outputpath

    width = pd.read_csv('{}'.format(widthpath), header=None).values
    length = 4
    test = Calculator(period, skiprow, width, length, thickness)
    mobility, on_off_ratio = test.fileReader(datapath, outputpath)
    print(mobility)
    print('\n')
    print(on_off_ratio)
    print('\n')
    response = input('Do you want to get the plot?\n')
    if response.lower().strip() == 'yes':
        test.plot(datapath)
    else:
        print('\n###Done###\n')
        return


if __name__ == "__main__":
    print('\nWELCOME!\n')
    print('--Version: 0.1    \n--Developed by Shengjie\n')

    # diaplay previous setting
    print('\nPrevious Setting\n')
    currentline = []
    try:
        with open('defaultParameter.txt', 'r') as text:
            for line in text:
                currentline = line.split(',')
        print(currentline)
        path, width, output, period, skiprow, thickness = currentline[0], currentline[1], currentline[2], int(
            currentline[3]), int(currentline[4]), int(currentline[5])

        print('data folder: \n', path)
        print('width file: \n', width)
        print('output file:\n', output)
        print('period: \n', period)
        print('skiprow: \n', skiprow)
        print('thickness: \n', thickness)
        question = input('Do you need to start new sesseion?')
        if question.lower().strip() == 'yes':
            path = input('data file path:  ').strip()
            csv = []
            dir = os.path.join("{}".format(path))
            print('\n')
            print('###File Searching###')
            for root, dirs, files in os.walk(dir):
                for file in files:
                    if file[-1] == 'v':
                        csv.append(file)
                        print("{}".format(csv[-1]))
            print('Total file: {}'.format(len(csv)))
            print('\n')
            width = input(
                'channel file path (end with .csv file):  ').strip()
            df = pd.read_csv(width, header=None)
            print((df.head()))
            print('\n')
            output = (input('result output:  ')).strip()
            print('\n')
            period = int(input('peroid:  (21?)'))
            print('\n')
            skiprow = int(input('skiprow:  (259?)'))
            print('\n')
            thickness = int(input('thickness: '))
            print('\n')
            # update the text
            with open('defaultParameter.txt', 'w+') as text:
                text.write('{},{},{},{},{}.{}'.format(
                    path, width, output, period, skiprow, thickness))
    except:
        question = input('Need new parameters...')
        path = input('data file path:  ').strip()
        csv = []
        dir = os.path.join("{}".format(path))
        print('\n')
        print('###File Searching###')
        for root, dirs, files in os.walk(dir):
            for file in files:
                if file[-1] == 'v':
                    csv.append(file)
                    print("{}".format(csv[-1]))
        print('Total file: {}'.format(len(csv)))
        print('\n')
        width = input('channel file path (end with .csv file):  ').strip()
        df = pd.read_csv(width, header=None)
        print((df.head()))
        print('\n')
        output = (input('result output:  ')).strip()
        print('\n')
        period = int(input('peroid:  (21?)'))
        print('\n')
        skiprow = int(input('skiprow:  (259?)'))
        print('\n')
        thickness = int(input('thickness: '))
        print('\n')
        # update the text
        with open('defaultParameter.txt', 'w+') as text:
            text.write('{},{},{},{},{},{}'.format(
                path, width, output, period, skiprow, thickness))
    run(path, width, output, period, skiprow, thickness)
