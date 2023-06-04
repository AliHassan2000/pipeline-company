import time

file_name = time.strftime("%d-%m-%Y")
try:    
    file = open('D:\\test-repo\\flask\\app\\failed\\ims\\'+file_name+'.txt','a',encoding='utf-8')
    file.write(file_name) 
    file.write('\nhi')
    print(file)
    file.close()
except Exception as e:
    print(e)
    print('Error! ',file_name,' file cannot be created.')
    
    
