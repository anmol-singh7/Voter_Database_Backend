# take a dir adderss and the destination address take all pdf from target dir
# and convert it into image store into a destionation dir then
# convert all img from all the dir present in destination dir into text file and stroe them into text_folder
# take all the txt file from there respective dir one by one an refine them and store them into a new dir'
import pytesseract
from PIL import Image
import os
import cv2
import numpy as np
from pdf2image import convert_from_path
import re
import pymongo
import json

client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
mydb = client["Voter_list"]
information = mydb.Voters

# import os
# pip install pdf2images
# path of folder from where pdfs are to be extracted

your_folder_path_of_pdfs = 'C:\Project\Pdfs3'
index = your_folder_path_of_pdfs.rindex("\\")
main_address = your_folder_path_of_pdfs[:index]
destination_of_img = main_address+"/"+"Images"
if not os.path.exists(destination_of_img):
    os.mkdir(destination_of_img)
text_folder = main_address+"/"+"Text files"
if not os.path.exists(text_folder):
    os.mkdir(text_folder)

# Main_text_folder = main_address+"/"+"Main_text_folder"
# if not os.path.exists(Main_text_folder):
#     os.mkdir(Main_text_folder)


def convert_pdf_to_jpg(file, outputDir):
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)
    else:
        list_of_files_to_be_remove = os.listdir(outputDir)
        for remove_file in list_of_files_to_be_remove:
            os.remove(outputDir+"/"+remove_file)
    pages = convert_from_path(file, 500)
    counter = 1
    for page in pages:
        myfile = outputDir+str(counter)+'.jpg'
        counter = counter+1
        page.save(myfile, "JPEG")


myconfig = r"--psm 11 --oem 3"


def refine_first_image_text(text):
    ConNum = ""
    ConName = ""
    PartNo = ""
    file = open(text_folder+"/1.txt", "w")
    file.write(text)
    file.close()
    file2 = open(text_folder+"/1.txt", "r")
    x = file2.readlines()
    # print(x)
    PartNo = PartNo+x[1].strip("\n")
    a = x[2]
    my_new_string = re.sub('[^a-zA-Z0-9 \n]', '', a)
    flag_for_Con_num_may_with_initial_space = True
    flag_for_Con_Num = True
    for i in range(len(my_new_string)):
        if my_new_string[i].isnumeric() and flag_for_Con_num_may_with_initial_space:
            flag_for_Con_num_may_with_initial_space = False
            ConAndName = my_new_string[i:]
            for k in range(len(ConAndName)):
                if not ConAndName[k].isnumeric() and flag_for_Con_Num:
                    flag_for_Con_Num = False
                    ConNum = ConNum+ConAndName[:k+1]
                    ConName_may_with_initial_space = ConAndName[k+1:]
                    for z in range(len(ConName_may_with_initial_space)):
                        if ConName_may_with_initial_space[z] != " ":
                            ConName = ConName + \
                                ConName_may_with_initial_space[z:].strip("\n")
                            break
    final_top_text = "PartNo:"+PartNo+"\n" + "ConNum:" + \
        ConNum+"\n"+"ConName:"+'"'+ConName+'"'+"\n"
    # final_top_text =""
    # top_file = open("2.txt", "w")
    # top_file.write("PartNo:"+PartNo+"\n")
    # top_file.write("ConNum:"+ConNum+"\n")
    # top_file.write("ConName:"+ConName+"\n")
    p=3
    while p< len(x):
        if  x[p].startswith("1.") or x[p].startswith("2.") or x[p].startswith("3.") or x[p].startswith("4.") or x[p].startswith("5.") or x[p].startswith("6.") or x[p].startswith("7.") or x[p].startswith("8.") or x[p].startswith("9."):
            final_top_text = final_top_text+x[p]
            q=p+1
            while q<len(x):
                if not x[q].startswith("1.") and not x[q].startswith("2.") and not x[q].startswith("3.") and not x[q].startswith("4.") and not x[q].startswith("5.") and not x[q].startswith("6.") and not x[q].startswith("7.") and not x[q].startswith("8.") and not x[q].startswith("9."):
                    final_top_text = final_top_text[:-1] +x[q]
                else:
                    p=q-1
                    break
                q=q+1    
        p=p+1
               
    file2.close()
    os.remove(text_folder+"/1.txt")
    return final_top_text, ConNum, ConName, PartNo


def refine_img_top(text_head):
    sec_top = open(text_folder+"/1.txt", "w")
    sec_top.write(text_head)
    sec_top.close()
    copy = open(text_folder+"/1.txt", "r")

    SecName = ""
    SecNo = ""
    for line in copy:
        a = line
        my_new_string = line
        for i in range(len(my_new_string)):
            if (~my_new_string[i].isnumeric() or ~my_new_string[i].isalpha()):
                continue
            else:
                my_new_string = my_new_string[i:]
                break
        if (my_new_string.startswith("Section No and Name")):
            w = True
            for i in range(len(my_new_string)):
                if my_new_string[i].isnumeric() and w:
                    w = False
                    NameAndNum = my_new_string[i:]
                    for k in range(len(NameAndNum)):
                        if ~NameAndNum[k].isnumeric():
                            SecNo = NameAndNum[:k+1]

                            SecNametrail = NameAndNum[k+1:]
                            l = 0
                            while l < len(SecNametrail)-1:
                                if not SecNametrail[l].isnumeric() and not SecNametrail[l].isalpha():
                                    l = l+1
                                    continue
                                else:
                                    SecName = SecNametrail[l:]
                                    break
                                l = l+1
                            break
    copy.close()
    os.remove(text_folder+"/1.txt")
    return SecName.strip("\n"), SecNo


def convert_first_img(first_img_path):
    parent = cv2.imread(first_img_path)
    myconfig = r"--psm 11 --oem 3"
    text2 = ""
    gray = cv2.cvtColor(parent, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 10))
    dilate = cv2.dilate(thresh, kernel, iterations=1)
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if h > 900 and w > 0:
            # print(y,y+h,x,x+w)
            roi = parent[y-5:y+h, x:x+w]
            cv2.imwrite(first_img_path, roi)
            cv2.rectangle(parent, (x, y), (x+w, y+h), (36, 255, 12), 2)

    image = cv2.imread(first_img_path)
    height, width = image.shape[:2]
    top_right = image[5:225, 3000:width]
    text3 = pytesseract.image_to_string(top_right)
    top_parent = image[0:230, 0:3000]
    # cv2.imwrite("12.jpg", top_parent)
    text2 = pytesseract.image_to_string(top_parent)
    # print(text2)
    text3 = text3+text2
    crop_parent = image[1470:2890, 0:1580]
    text = pytesseract.image_to_string(crop_parent, config=myconfig)
    text3 = text3+text
    # print(text3)
    return text3


def unrefined_to_refined(Input_path):
    # dir_path = text_folder+"/"+text_dir
    # text_list = os.listdir(dir_path)
    # print(text_list)
    # print("\n")
    text_to_write = ""
    # if not os.path.exists(Output_path):
    #    os.mkdir(Output_path)
    # text_file = open(Output_path+"final.txt", "w")

    # for text in text_list:
    file = open(Input_path, "r")

    i = 0
    content = file.readlines()
    while i < len(content):
        if content[i].startswith("Pho") or content[i].startswith("Avail") or content[i].startswith("\n"):
            i = i+1
            continue

        elif content[i].startswith('"VoterId"'):
            j = i+1
            ans = content[i].replace('"VoterId"', "")
            while j < len(content):
                if content[j].startswith("Pho") or content[j].startswith("Avail") or content[j].startswith("\n"):
                    j = j+1
                    continue
                elif content[j].startswith("Name") or content[j].startswith("Husband's Name") or content[j].startswith("Father's Name") or content[j].startswith("Mother's Name") or content[j].startswith("House Number") or content[j].startswith("Age") or content[j].startswith("Sex"):
                    break
                elif  content[j].startswith("}"):
                    text_to_write = text_to_write+ans.strip(",")
                else:
                    ans = ans.replace("\n", "") + " " + \
                        content[j].replace("\n", "")+" "
                    j = j+1

            my_new_ans = re.sub('[^a-zA-Z0-9\n]', '', ans)
            ans = my_new_ans[-10:]
            ans = '"VoterId":"'+ans
            text_to_write = text_to_write+ans.strip("\n")+'",\n'
            # text_file.write(ans[:-1]+'",\n')
            i = j-1

        elif content[i].startswith("House Number"):
            j = i+1
            ans = content[i].replace("House Number", "")
            while j < len(content):
                if content[j].startswith("Pho") or content[j].startswith("Avail") or content[j].startswith("\n"):
                    j = j+1
                    continue
                elif content[j].startswith("Name") or content[j].startswith("Husband's Name") or content[j].startswith("Father's Name") or content[j].startswith("Mother's Name") or content[j].startswith("VoterId") or content[j].startswith("Age") or content[j].startswith("Sex"):
                    break
                elif content[j].startswith("}"):
                    text_to_write = text_to_write+ans.strip(",")
                else:
                    ans = ans.replace("\n", "") + " " + \
                        content[j].replace("\n", "")+" "
                    j = j+1

            w = True
            t = 0
            while t < len(ans):
                if ans[t] == " ":
                    t = t+1
                    continue
                else:
                    ans = ans[t:]
                    # w = False
                    break
            q = 0
            while q < len(ans):
                if ~ans[q].isalpha() and ~ans[q].isnumeric():
                    t = q+1
                    while t < len(ans):
                        if ans[t] == " ":
                            t = t+1
                            continue
                        else:
                            ans = ans[t:]
                            w = False
                            break
                if ~w:
                    break
                q = q+1
            ans = '"Address": "House Number '+ans
            text_to_write = text_to_write+ans.replace("\n", "")+'",\n'
            # text_file.write(ans.replace("\n", "")+'",')
            i = j-1

        elif content[i].startswith("Father"):
            j = i+1
            ans = content[i].replace("Father's Name", "")
            while j < len(content):
                if content[j].startswith("Pho") or content[j].startswith("Avail") or content[j].startswith("\n"):
                    j = j+1
                    continue
                elif content[j].startswith("Name") or content[j].startswith("Husband's Name") or content[j].startswith("VoterId") or content[j].startswith("Mother's Name") or content[j].startswith("House Number") or content[j].startswith("Age") or content[j].startswith("Sex"):
                    break
                elif content[j].startswith("}"):
                    text_to_write = text_to_write+ans.strip(",")
                else:
                    ans = ans.replace("\n", "") + " " + \
                        content[j].replace("\n", "")+" "
                    j = j+1
            my_new_ans = re.sub('[^a-zA-Z0-9 \n]', '', ans)
            qq = 0
            while qq < len(my_new_ans):
                if my_new_ans[qq] == " ":
                    qq = qq+1
                    continue
                else:
                    ans = my_new_ans[qq:]
                    break
                qq = qq+1
            ans = '"FatherName":"'+ans
            text_to_write = text_to_write+ans.replace("\n", "")+'",\n'
            # text_file.write(ans.replace("\n", "")+'",')
            i = j-1

        elif content[i].startswith("Mother"):
            j = i+1
            ans = content[i].replace("Mother's Name", "")
            while j < len(content):
                if content[j].startswith("Pho") or content[j].startswith("Avail") or content[j].startswith("\n"):
                    j = j+1
                    continue
                elif content[j].startswith("Name") or content[j].startswith("Husband's Name") or content[j].startswith("Father's Name") or content[j].startswith("VoterId") or content[j].startswith("House Number") or content[j].startswith("Age") or content[j].startswith("Sex"):
                    break
                elif content[j].startswith("}"):
                    text_to_write = text_to_write+ans.strip(",")
                else:
                    ans = ans.replace("\n", "") + " " + \
                        content[j].replace("\n", "")+" "
                    j = j+1

            my_new_ans = re.sub('[^a-zA-Z0-9 \n]', '', ans)
            qq = 0
            while qq < len(my_new_ans):
                if my_new_ans[qq] == " ":
                    qq = qq+1
                    continue
                else:
                    ans = my_new_ans[qq:]
                    break
                qq = qq+1

            ans = '"MotherName":"'+ans
            text_to_write = text_to_write+ans.replace("\n", "")+'",\n'
            # text_file.write(ans.replace("\n", "")+'",')
            i = j-1

        elif content[i].startswith("Husband"):
            j = i+1
            ans = content[i].replace("Husband's Name", "")
            while j < len(content):
                if content[j].startswith("Pho") or content[j].startswith("Avail") or content[j].startswith("\n"):
                    j = j+1
                    continue
                elif content[j].startswith("Name") or content[j].startswith("VoterId") or content[j].startswith("Father's Name") or content[j].startswith("Mother's Name") or content[j].startswith("House Number") or content[j].startswith("Age") or content[j].startswith("Sex"):
                    break
                elif content[j].startswith("}"):
                    text_to_write = text_to_write+ans.strip(",")
                else:
                    ans = ans.replace("\n", "") + " " + \
                        content[j].replace("\n", "")+" "
                    j = j+1

            my_new_ans = re.sub('[^a-zA-Z0-9 \n]', '', ans)
            qq = 0
            while qq < len(my_new_ans):
                if my_new_ans[qq] == " ":
                    qq = qq+1
                    continue
                else:
                    ans = my_new_ans[qq:]
                    break
                qq = qq+1

            ans = '"HusbandName":"'+ans
            text_to_write = text_to_write+ans.replace("\n", "")+'",\n'
            # text_file.write(ans.replace("\n", "")+'",')
            i = j-1

        elif content[i].startswith("Name"):
            j = i+1
            ans = content[i].replace("Name", "")
            while j < len(content):
                if content[j].startswith("Pho") or content[j].startswith("Avail") or content[j].startswith("\n"):
                    j = j+1
                    continue
                elif content[j].startswith("VoterId") or content[j].startswith("Husband's Name") or content[j].startswith("Father's Name") or content[j].startswith("Mother's Name") or content[j].startswith("House Number") or content[j].startswith("Age") or content[j].startswith("Sex"):
                    break
                elif content[j].startswith("}"):
                    text_to_write = text_to_write+ans.strip(",")
                else:
                    ans = ans.replace("\n", "") + " " + \
                        content[j].replace("\n", "")+" "
                    j = j+1
            my_new_ans = re.sub('[^a-zA-Z0-9 \n]', '', ans)
            qq = 0
            while qq < len(my_new_ans):
                if my_new_ans[qq] == " ":
                    qq = qq+1
                    continue
                else:
                    ans = my_new_ans[qq:]
                    break
                qq = qq+1

            ans = '"Name":"'+ans
            text_to_write = text_to_write+ans.replace("\n", "")+'",\n'
            # text_file.write(ans.replace("\n", "")+'",')
            i = j-1

        elif content[i].startswith('"PartNo"'):
            text_to_write = text_to_write+content[i].replace("\n", ",\n")
            # text_file.write(content[i].replace("\n", ",\n"))
        elif content[i].startswith('"ConNum"'):
            text_to_write = text_to_write+content[i].replace("\n", ",\n")
            # text_file.write(content[i].replace("\n", ",\n"))
        elif content[i].startswith('"ConName"'):
            text_to_write = text_to_write+content[i].replace("\n", ",\n")
            # text_file.write(content[i].replace("\n", ",\n"))
        elif content[i].startswith('"SecNo"'):
            text_to_write = text_to_write+content[i].replace("\n", ",\n")
            # text_file.write(content[i].replace("\n", ",\n"))
        elif content[i].startswith('"SecName"'):
            text_to_write = text_to_write+content[i].replace("\n", ",\n")
            # text_file.write(content[i].replace("\n", ",\n"))
        elif content[i].startswith('"SrNo"'):
            text_to_write = text_to_write+content[i].replace("\n", ",\n")
            # text_file.write(content[i].replace("\n", ",\n"))

        elif content[i].startswith("Age"):
            index = content[i].rfind("S")
            if index!=-1:
                  text_to_write = text_to_write + \
                      content[i][:index-1].replace("Age", '"Age"') + ",\n"
                  # text_file.write(content[i][:index-1].replace("Age", '"Age"') + ",")
                  sex = content[i][index:]
                  sexindex = sex.find("M")
                  if (sexindex != -1):
                      text_to_write = text_to_write + '"Sex":"MALE"\n'
                     # text_file.write('"Sex":"MALE"')Frefine 
                  else:
                      text_to_write = text_to_write + '"Sex":"FEMALE"\n'
                      # text_file.write('"Sex":"FEMALE"')
            else:
                
                # print(content[i])
                i=i+1
                continue

        else:
            text_to_write = text_to_write + content[i]
            # text_file.write(content[i])
        i = i+1
    # file.close()
    # list_of_files_to_be_remove = os.listdir(Output_path)
    # for remove_file in list_of_files_to_be_remove:
    #     os.remove(Input_path+remove_file)
    # os.rmdir(Input_path)

    # text_file.close()
    return text_to_write


def convert_img_to_text(image_path, counter, ConNum, ConName, PartNo):
    ConstNumb = "0"
    if ConNum != "":
        ConstNumb = ConNum
    count = int(counter)
    parent = cv2.imread(image_path)
    myconfig = r"--psm 11 --oem 3"

    base_image = parent.copy()
    coordinates_of_top_line = 0

    base_image = parent.copy()
    gray = cv2.cvtColor(parent, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (100, 10))
    dilate = cv2.dilate(thresh, kernel, iterations=1)
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if h > 900 and w > 0:
            coordinates_of_top_line = y
            roi = parent[y:y+h, x:x+w]
            cv2.imwrite(image_path, roi)
            cv2.rectangle(parent, (x, y), (x+w, y+h), (36, 255, 12), 2)

    newim = cv2.imread(image_path)
    height, width = newim.shape[:2]
    # print(height, width)
    py = 4
    height_divider = int((height+200)/486)
    width_divider = int((width+600)/1256)
    # print(height_divider)
    cw = int((width-30)/width_divider)
    ch = int((height-10)/height_divider)
    # t = 1
    # file = open("C:\Project\\test\processing/1.txt", "w")
    top_parent = base_image[0:coordinates_of_top_line, 0:width]
    # text2 = "\nHEAD_START\n"

    text_head = pytesseract.image_to_string(top_parent, config=myconfig)
    SecName, SecNo = refine_img_top(text_head)
    final_text = ""
    for j in range(1, 11):
        px = 16
        for i in range(1, 4):
            crop_parent = newim[py:py+ch, px:px+cw]
            top_left_corner = crop_parent[0:75, 60:600]
            base_image = top_left_corner.copy()
            gray = cv2.cvtColor(top_left_corner, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (7, 7), 0)
            thresh = cv2.threshold(
                blur, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 50))
            dilate = cv2.dilate(thresh, kernel, iterations=1)
            cnts = cv2.findContours(
                dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])
            for c in cnts:
                x, y, w, h = cv2.boundingRect(c)
                if h > 0 and w > 0:
                    coordinates_of_top_line = y
                    roi = top_left_corner[y:y+h, x:x+w]
                    #   cv2.imwrite("E:\\ft", roi)
                    #   cv2.imshow("hi",roi)
                    #   cv2.waitKey(0)
                    #   cv2.imwrite("E:/24.jpg", roi)
                    cv2.rectangle(crop_parent, (x, y), (x+w, y+h),
                                  (36, 255, 12), 2)
            top_left_text = pytesseract.image_to_string(roi)
            # print(top_left_text)
            # print(text)
            #    cv2.imwrite("C:\Project\croped/"+str(t)+".jpg", crop_parent)
            # x = 0
            # final_top_left_text = ""
            # while x < len(top_left_text):
            #        if top_left_text[x].isnumeric() or top_left_text[x].isalpha() or top_left_text[x] == "$" or top_left_text[x] == "-":
            #            final_top_left_text = final_top_left_text +top_left_text[x]
            #        x=x+1
            #    t = t+1
            # print(count, final_top_left_text)
            text = pytesseract.image_to_string(crop_parent, config=myconfig)
            if text != "":
                text2 = "{\n"+'"ConNum":'+ConstNumb+"\n"+'"ConName":'+'"'+ConName+'"'+"\n"+'"PartNo":'+PartNo+"\n" + \
                    '"SecNo":'+SecNo+"\n"+'"SecName":'+'"'+SecName+'"'+"\n" + \
                    '"SrNo":'+str(count)+"\n"+'"VoterId":' + '"'+text+"\n},\n"
                file = open(main_address+"/temp2.txt", "w")
                file.write(text2)
                file.close()
                final_text_chunk = unrefined_to_refined(
                    main_address+"/temp2.txt")
                final_text = final_text+final_text_chunk
                count = count+1
            px = px+cw
        py = py+ch
        os.remove(main_address+"/temp2.txt")
    return final_text, count


# pdf_number=0
list_of_files = os.listdir(your_folder_path_of_pdfs)
for your_file_name in list_of_files:
    # pdf_number=pdf_number+1
    counter = 1
    ConNum = ""
    ConName = ""
    PartNo = ""
    path_of_folder = destination_of_img+'/'+your_file_name+'/'
    convert_pdf_to_jpg(your_folder_path_of_pdfs+'/' +
                       your_file_name, path_of_folder)
    if not os.path.exists(text_folder+"/"+your_file_name+"/"):
        os.mkdir(text_folder+"/"+your_file_name+"/")
    else:
        list_of_files_to_be_remove = os.listdir(
            text_folder+"/"+your_file_name+"/")
        for remove_file in list_of_files_to_be_remove:
            os.remove(text_folder+"/"+your_file_name+"/"+remove_file)
    list_of_files = os.listdir(path_of_folder)
    i = 0
    file = open(text_folder+"/"+your_file_name+"/"+"final"+".txt", "w")
    for file_number in range(1, len(list_of_files)):
        i = i+1

        # text_path = text_folder+"/"+your_file_name+"/"+str(file_number)+".txt"
        if i == 1:
            first_img_path = path_of_folder+str(file_number)+".jpg"
            text = convert_first_img(first_img_path)
            final_first_text, ConNum, ConName, PartNo = refine_first_image_text(
                text)
            # os.remove(path_of_folder+str(file_number)+".jpg")
            # file = open(text_path, "w")
            # file.write(final_first_text)
        elif i == 2:
            continue
        else:
            # img = Image.open(path_of_folder+your_pic_name)
            image_path = path_of_folder+str(file_number)+".jpg"
            # text = pytesseract.image_to_string(img)
            text, counter = convert_img_to_text(
                image_path, counter, ConNum, ConName, PartNo)
            # file = open(text_path, "w")
            file.write(text+"\n")
    file.close()
    list_of_files_to_be_remove = os.listdir(path_of_folder)
    for remove_file in list_of_files_to_be_remove:
        os.remove(path_of_folder+remove_file)
    os.rmdir(path_of_folder)

    # unrefined_to_refined(text_folder+"/"+your_file_name +"/", Main_text_folder+"/"+your_file_name+"/")
os.rmdir(destination_of_img)
# os.rmdir(text_folder)


list_of_final_txt_dir = os.listdir(text_folder)
for txt_folder in list_of_final_txt_dir:
    final = open(text_folder+"/"+txt_folder+"/"+"final.txt", "r")
    text = ""
    for line in final:
        text = text+line
    text = text[:-1]
    parsed = json.loads('['+text+']')
    information.insert_many(parsed)
    final.close()
