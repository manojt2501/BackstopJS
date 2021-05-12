import os
import json
import shutil
from pdf2image import convert_from_path
import configparser

def main():
    Config = configparser.ConfigParser()
    Config.read(r"read.ini")
    BSpath = dict(Config.items('BS'))
    testPath = dict(Config.items('input'))             #reading config to check the path to initialize backstop
    outputPath = dict(Config.items('output'))
    shutil.rmtree(BSpath['path']+'\\backstop_data')
    os.chdir(BSpath['path'])
    os.system("backstop init")   #changing directory and initializing backstop
    json_path = BSpath['path']+'\\backstop.json'
    with open(json_path) as f:
        data = json.load(f)    #reading backstop json and loading it to data
    Profile_list = os.listdir(testPath['path'])   #assinging value to variable of the directory inside
    for profile in Profile_list:
        profile_path = testPath['path'] + "\\" + profile
        image_list = os.listdir(profile_path)
        ref = [y for y in image_list if 'ref' in y][0]
        test = [y for y in image_list if 'test' in y][0]
        pdf2img(ref, profile_path)
        pdf2img(test, profile_path)  # verifying the list of folder and the pdf. then converting pages to image
        img_refPath = "file:///" + profile_path.replace('\\', '/') + "/" + str(ref).replace('.pdf', '.jpg')
        img_testPath = "file:///" + profile_path.replace('\\', '/') + "/" + str(test).replace('.pdf', '.jpg')
        data['scenarios'][0]['label'] = profile
        data['scenarios'][0]['referenceUrl'] = img_refPath
        data['scenarios'][0]['url'] = img_testPath
        a_file = open(BSpath['path'] + '\\backstop.json', "w")
        json.dump(data, a_file)
        a_file.close()
        os.chdir(BSpath['path'])
        os.system("backstop reference")
        os.system("backstop test")
        resultPath = BSpath['path'] + '\\backstop_data\\bitmaps_test'
        resultFolder = os.listdir(resultPath)
        reportJSON = BSpath['path'] + '\\backstop_data\\bitmaps_test\\' + resultFolder[0] + '\\report.json'
        with open(reportJSON) as f:
            dataReport = json.load(f)
        label = dataReport['tests'][0]['pair']['label']
        status = dataReport['tests'][0]['status']
        source = BSpath['path'] + '\\backstop_data'
        destination = outputPath['path']
        shutil.copytree(source, destination + "\\" + label + "-" + status)
        shutil.rmtree(BSpath['path'] + '\\backstop_data\\bitmaps_test\\' + resultFolder[0])

def pdf2img(pdf_name,path):
    images = convert_from_path(path+'\\'+pdf_name)
    os.chdir(path)
    for i in range(len(images)):
        images[i].save(pdf_name.split('.')[0]+'.jpg', 'JPEG')

if __name__ == '__main__':
    main()