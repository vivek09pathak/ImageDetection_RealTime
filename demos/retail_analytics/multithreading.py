#!/usr/bin/env python
# from threading import Thread
import csv
import time
import requests
from threading import Thread
from flask_cors import CORS
from flask import request,jsonify
from flask import Flask, render_template, Response
import cv2
import numpy as np
import json
import threading
from data.demos.retail_analytics.inputs import path as input_path
from data.demos.retail_analytics.trained import path as model_path
from data.demos.retail_analytics.inputs import path as file_path

from demos.retail_analytics.frontend import YOLO
from demos.retail_analytics.utilities import draw_boxes
from tf_session.tf_session_utils import Pipe
import json
from keras import backend as K

app = Flask(__name__)
CORS(app)



class RetailAnalytics():
    _check = 0
    def __init__(self):
        self.rack_range=None
        self.horizontal_stacks=None
        self.vertical_stacks=None
        self.shelfs_matrix = None
        self.left_x=None
        self.right_x=None
        self.top_y=None
        self.bottom_y=None
        self.shelf_vsize=None
        self.shelf_hsize=None
        self.detergent_range=None
        self.mineralWater_range=None
        self.biscuit_range=None
        self.lays_range=None
        self.noodles_range=None
        self.coke_range=None
        self.product_range={}
        self.shelf_dict={}
        self.labels_dict=None
        self.labels=[]
        self.shelf_state={}
        self.yolo = None
        self.config = None
        self.shelf_product_type=None
        self.prev_shelf_state_1=None
        self.postjsondata = {}
        self.finaljsondata = {}
        self.check_flag = 0
        self.rack_dict=None

    def global_init(self,h_stack=3,vstack=2, session_runner=None):
        # print(dict)
        K.clear_session()
        self.config_path = input_path.get()+"/config.json"
        weights_path = model_path.get()+"/full_yolo_detergent_and_maggie.h5"
        rack_cord=None
        # print(self.rack_dict)
        if(self.rack_dict!=None):
            if(self.rack_dict['point_set_1']!=None):
                    rack_cord = self.rack_dict['point_set_1'].copy()
                    self.check_flag = 1

                    # print(self.rack_range)
                    temp=rack_cord[2]
                    rack_cord[2]=rack_cord[3]
                    rack_cord[3]=temp
        # print(self.check_flag )
        # print(rack_cord)
        # self.rack_range=[(400,205),(1150,205),(400,700),(1150,700)]
        # self.rack_range=[[428,202],[1143,212],[1116,682],[469,682]]
        if(self.check_flag==1):

            self.horizontal_stacks=h_stack
            self.vertical_stacks=vstack
            self.shelfs_matrix = [[None for x in range(self.vertical_stacks)] for y in range(self.horizontal_stacks)]
            self.left_x=rack_cord[0][0]
            self.right_x=rack_cord[1][0]
            self.top_y=rack_cord[0][1]
            self.bottom_y=rack_cord[2][1]
            shelf_count=1
            self.shelf_vsize=(self.bottom_y-self.top_y)/self.horizontal_stacks
            self.shelf_hsize=(self.right_x-self.left_x)//self.vertical_stacks
            for i in range(0,self.horizontal_stacks):
                for j in range(0,self.vertical_stacks):
                    self.shelfs_matrix[i][j]=(j*self.shelf_hsize+self.left_x,i*self.shelf_vsize+self.top_y)
                    self.shelf_dict["shelf"+str(shelf_count)]=(j*self.shelf_hsize+self.left_x,i*self.shelf_vsize+self.top_y)
                    shelf_count+=1
            self.labels=[0,1,2,3,4,5]
            self.detergent_range=self.shelf_dict["shelf1"]
            self.mineralWater_range=self.shelf_dict["shelf2"]
            self.biscuit_range=self.shelf_dict["shelf3"]
            self.lays_range=self.shelf_dict["shelf4"]
            self.noodles_range=self.shelf_dict["shelf5"]
            self.coke_range=self.shelf_dict["shelf6"]
            self.labels_dict={1:"detergent",4:"noodles",0:"lays",2:"mineral_water",3:"coke",5:"biscuit"}
            self.product_range={2:self.mineralWater_range,1:self.detergent_range,5:self.biscuit_range,4:self.noodles_range,3:self.coke_range,0:self.lays_range}
            self.shelf_product_type=['detergent','mineral_water','biscuit','lays','noodles','coke']
            #model Load
            with open(self.config_path) as config_buffer:
                self.config = json.load(config_buffer)
            self.yolo = YOLO(backend=self.config['model']['backend'],
                        input_size=self.config['model']['input_size'],
                        labels=self.config['model']['labels'],
                        max_box_per_image=self.config['model']['max_box_per_image'],
                        anchors=self.config['model']['anchors'])
            print(weights_path)
            self.yolo.load_weights(weights_path)
            print("successfull")
            return True
        else:
            return False

    def global_init_1(self,h_stack=1,vstack=1, session_runner=None):
        # print(dict)
        K.clear_session()
        self.config_path = input_path.get()+"/config.json"
        weights_path = model_path.get()+"/full_yolo_detergent_and_maggie.h5"
        rack_cord=None
        # print(self.rack_dict)
        if(self.rack_dict!=None):
            if(self.rack_dict['point_set_1']!=None):
                    rack_cord = self.rack_dict['point_set_1'].copy()
                    self.check_flag = 1

                    # print(self.rack_range)
                    temp=rack_cord[2]
                    rack_cord[2]=rack_cord[3]
                    rack_cord[3]=temp
        # print(self.check_flag )
        # print(rack_cord)
        # self.rack_range=[(400,205),(1150,205),(400,700),(1150,700)]
        # self.rack_range=[[428,202],[1143,212],[1116,682],[469,682]]
        if(self.check_flag==1):

            self.horizontal_stacks=h_stack
            self.vertical_stacks=vstack
            self.shelfs_matrix = [[None for x in range(self.vertical_stacks)] for y in range(self.horizontal_stacks)]
            self.left_x=rack_cord[0][0]
            self.right_x=rack_cord[1][0]
            self.top_y=rack_cord[0][1]
            self.bottom_y=rack_cord[2][1]
            shelf_count=1
            self.shelf_vsize=(self.bottom_y-self.top_y)/self.horizontal_stacks
            self.shelf_hsize=(self.right_x-self.left_x)//self.vertical_stacks
            for i in range(0,self.horizontal_stacks):
                for j in range(0,self.vertical_stacks):
                    self.shelfs_matrix[i][j]=(j*self.shelf_hsize+self.left_x,i*self.shelf_vsize+self.top_y)
                    self.shelf_dict["shelf"+str(shelf_count)]=(j*self.shelf_hsize+self.left_x,i*self.shelf_vsize+self.top_y)
                    shelf_count+=1
            self.labels=[0,1,2,3,4,5]
            mis_range=self.shelf_dict["shelf1"]
            change_in_range=(mis_range[0]+self.shelf_hsize,mis_range[1]+self.shelf_vsize)
            self.detergent_range=change_in_range
            self.mineralWater_range=change_in_range
            self.biscuit_range=change_in_range
            self.lays_range=change_in_range
            self.coke_range=self.shelf_dict["shelf1"]
            self.labels_dict={1:"detergent",4:"noodles",0:"lays",2:"mineral_water",3:"coke",5:"biscuit"}
            self.product_range={2:self.mineralWater_range,1:self.detergent_range,5:self.biscuit_range,4:self.noodles_range,3:self.coke_range,0:self.lays_range}
            self.shelf_product_type=['detergent','mineral_water','biscuit','lays','noodles','coke']
            #model Load
            with open(self.config_path) as config_buffer:
                self.config = json.load(config_buffer)
            self.yolo = YOLO(backend=self.config['model']['backend'],
                        input_size=self.config['model']['input_size'],
                        labels=self.config['model']['labels'],
                        max_box_per_image=self.config['model']['max_box_per_image'],
                        anchors=self.config['model']['anchors'])
            print(weights_path)
            self.yolo.load_weights(weights_path)
            print("successfull")
            return True
        else:
            return False

    def get_ycordinates(self,box,image_h, image_w):
        return int(box.ymin*image_h),int(box.ymax*image_h)

    def get_xcordinates(self,box,image_h, image_w):
        return int(box.xmin*image_w),int(box.xmax*image_w)

    def misplacedBoxes(self,boxes,image):
        image_h, image_w, _ = image.shape
        misplaced=[]

        for shelf_no,shelf_range  in self.shelf_dict.items():
            for box in boxes:
                ymin,ymax=self.get_ycordinates(box,image_h, image_w)
                xmin,xmax=self.get_xcordinates(box,image_h, image_w)
                centery=(ymin+ymax)/2-5
                centerx=(xmin+xmax)/2
                label=box.get_label()
                if(label in self.labels):
                    if not ((self.product_range[label][1]<centery<self.product_range[label][1]+self.shelf_vsize) and
                            (self.product_range[label][0]<centerx<self.product_range[label][0]+self.shelf_hsize  ) ):
                        if(box not in misplaced):
                            misplaced.append(box)


                    if((shelf_range[1]<centery<shelf_range[1]+self.shelf_vsize) and
                            (shelf_range[0]<centerx<shelf_range[0]+self.shelf_hsize)):
                            # self.shelf_state[shelf_no]['products'].append(self.self.labels_dict[label])

                            if not ((self.product_range[label][1]<centery<self.product_range[label][1]+self.shelf_vsize) and
                            (self.product_range[label][0]<centerx<self.product_range[label][0]+self.shelf_hsize  ) ):
                                # self.shelf_state[shelf_no]['misplaced'].append(self.self.labels_dict[label])
                                # print(self.shelf_state)
                                if self.labels_dict[box.get_label()] in self.shelf_state[shelf_no]['misplaced']:
                                    self.shelf_state[shelf_no]['misplaced'][self.labels_dict[box.get_label()]]+=1
                                else:
                                    self.shelf_state[shelf_no]['misplaced'][self.labels_dict[box.get_label()]] = 1
                            else:
                                # print(type(self.shelf_state[shelf_no]['products']))
                                if self.labels_dict[box.get_label()] in self.shelf_state[shelf_no]['products']:
                                    self.shelf_state[shelf_no]['products'][self.labels_dict[box.get_label()]] += 1
                                else:
                                    self.shelf_state[shelf_no]['products'][self.labels_dict[box.get_label()]] = 1



                    # if(shelf_no=='shelf3'):
                    #     cv2.putText(image,
                    #     str(str(self.shelf_state[shelf_no]['misplaced'])),
                    #         (400,120 ),
                    #         cv2.FONT_HERSHEY_SIMPLEX,
                    #         1e-3 * image_h,
                    #         (0,0,255), 3)
                    #     cv2.putText(image,
                    #     str(self.shelf_state[shelf_no]['products']),
                    #         (400,170 ),
                    #         cv2.FONT_HERSHEY_SIMPLEX,
                    #         1e-3 * image_h,
                    #         (0,255,0), 3)

        image=self.draw_box_misplaced(image,misplaced)

        return image

    def draw_box_misplaced(self,image,misplaced):
        misplaced_str="misplaced items:"
        image_h, image_w, _ = image.shape
        for product in misplaced:
            misplaced_str+=self.labels_dict[product.get_label()]+","

            ymin,ymax=self.get_ycordinates(product,image_h, image_w)
            xmin,xmax=self.get_xcordinates(product,image_h, image_w)
            cv2.rectangle(image, (xmin,ymin), (xmax,ymax), (0,0,255), 3)
            cv2.putText(image,
                   misplaced_str,
                    (30,30 ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1e-3 * image_h*1.5,
                    (0,0,255), 3)
        return image
    def draw_empty_space(self,boxes,image):
        box_in_shelf=[]
        totalempty_percentage=[]
        image_h, image_w, _ = image.shape
        for shelf_no,shelf_range  in self.shelf_dict.items():
            empty_space=0
            box_xmin_shelf=[]
            box_xmax_shelf=[]
            for box in boxes:
                ymin,ymax=self.get_ycordinates(box,image_h, image_w)
                xmin,xmax=self.get_xcordinates(box,image_h, image_w)
                centery=(ymin+ymax)/2-5
                centerx=(xmin+xmax)/2
                if((shelf_range[1]<centery<shelf_range[1]+self.shelf_vsize) and
                      (shelf_range[0]<centerx<shelf_range[0]+self.shelf_hsize)):
                    box_xmin_shelf.append(xmin)
                    box_xmax_shelf.append(xmax)



            box_xmin_shelf.append(shelf_range[0]+self.shelf_hsize)
            box_xmax_shelf.append(shelf_range[0]+self.shelf_hsize)
            y_box=shelf_range[1]+5
            box_xmin_shelf.sort()
            box_xmax_shelf.sort()
            x_start=shelf_range[0]
            x_end=shelf_range[0]+self.shelf_hsize

            #draw boxes
            for i in range(0,len(box_xmin_shelf)):
                xmin=box_xmin_shelf[i]
                xmax=box_xmax_shelf[i]
                if(xmin-x_start>40):
                    cv2.rectangle(image, (int(x_start+5),int(y_box)),
                                  (int(xmin-5),int(y_box+self.shelf_vsize)), (255,0,0), 3)
                    empty_space+=xmin-x_start
                else:
                    empty_space+=xmin-x_start
                x_start=xmax
            empty_percentage=empty_space/self.shelf_hsize
            self.shelf_state[shelf_no]['perempty']=empty_percentage

        return image

    def print_shelfNo(self,image):
        shelf_count=1
        image_h, image_w, _ = image.shape
        for i in range(0,self.horizontal_stacks):
            for j in range(0,self.vertical_stacks):
                cv2.putText(image,
                    str(shelf_count),
                        (int(j*self.shelf_hsize+self.left_x+55),int(i*self.shelf_vsize+self.top_y+75) ),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1e-3 * image_h*1.5,
                        (0,0,255), 3)
                self.shelf_state['shelf'+str(shelf_count)]={'perempty':None,'misplaced':{},
                'products':{},
                'position':shelf_count-1,'product_type':self.shelf_product_type[shelf_count-1]}
                shelf_count+=1
        return image

    def change_of_state(self):
        flag = 0
        if (self.prev_shelf_state_1 == None):
            self.prev_shelf_state_1 = self.shelf_state
            flag = 1
        for i in range(1, len(self.shelf_dict) + 1):
            per = self.shelf_state['shelf' + str(i)]['perempty']
            pre_per = self.prev_shelf_state_1['shelf' + str(i)]['perempty']
            if (abs(pre_per - per) > 20):
                print("empty")
                flag = 1
                break
            current_list=self.shelf_state['shelf' + str(i)]['misplaced'].keys()
            previous_list=self.prev_shelf_state_1['shelf' + str(i)]['misplaced'].keys()
            count=0
            if (len(previous_list)==len(current_list)):
                for x in previous_list:
                    if x in current_list:
                        count+=1
            else:
                flag=1
                break
            if(count!=len(current_list)):
                flag=1
                break


        if (flag == 1):
            tempJson = []
            for i in self.shelf_state.keys():
                tempJson.append({"name":i,"value":self.shelf_state[i]})
            self.postjsondata = {'store':"store-2jmvt5t13",'rack':"rack-2jmvtheoo",'zone':"zone-2jmvts25j",'shelves':tempJson}
            # print(res)
            # s = json.dumps(self.postjsondata)
            print(self.postjsondata, ' ', RetailAnalytics._check, '\n')
            # open("out.json", "w").write(s+'\n')
            RetailAnalytics._check += 1
        self.prev_shelf_state_1 = self.shelf_state.copy()
        return flag

    def postdata(self):
        res = requests.post('https://us-central1-retailanalytics-d6ccf.cloudfunctions.net/api/misplaced-items',json=self.postjsondata)

class Pipeline():

    def __init__(self):
        self.object_model=RetailAnalytics()

    # def use_session_runner(self, session_runner):
    #     self.session_runner = session_runner


    def gen_analysis(self):

        print(self.object_model.rack_dict)
        self.object_model.rack_dict = dict
        check_rackfill=self.object_model.global_init()
        print(check_rackfill)
        if (check_rackfill):
            flag = True
            flag_in_pipe.push(flag)
            while True:
                image_in_pipe.wait()
                ret, image = image_in_pipe.pull()
                if not ret:
                    continue
                if(dict['point_set_2']!=None):

                    # M = cv2.getPerspectiveTransform(
                    #     np.array([[428, 202], [1143, 212], [1116, 682], [469, 682]], dtype="float32"),
                    #     np.array([[428, 202], [1143, 202], [1143, 682], [428, 682]], dtype="float32"))
                    # print(dict['point_set_1'])
                    # print(dict['point_set_2'])
                    test1 = np.array(dict['point_set_1'],dtype="float32")
                    test2 = np.array(dict['point_set_2'],dtype="float32")
                    M = cv2.getPerspectiveTransform(test1,test2)
                    image = cv2.warpPerspective(image, M, (image.shape[1],image.shape[0]))
                    boxes = self.object_model.yolo.predict(image)
                    image = draw_boxes(image, boxes, self.object_model.config['model']['labels'])
                    ret, zones = zone_detection_in_pipe.pull()

                    if ret and not zones:
                        image=self.object_model.print_shelfNo(image)
                        image=self.object_model.misplacedBoxes(boxes,image)
                        image=self.object_model.draw_empty_space(boxes,image)
                        flag = self.object_model.change_of_state()
                        if flag == 1:
                            # pass
                            Thread(target=self.object_model.postdata).start()
                    yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', image)[1].tostring() + b'\r\n')

    def gen_tracking(self):
        while True:
            tracking_in_pipe.wait()
            ret, image = tracking_in_pipe.pull()
            if not ret:
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', image)[1].tostring() + b'\r\n')

    def gen_age_api(self):
        while True:
            age_in_pipe.wait()
            ret, image = age_in_pipe.pull()
            if not ret:
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', image)[1].tostring() + b'\r\n')


image_in_pipe = Pipe()
tracking_in_pipe = Pipe()
age_in_pipe = Pipe()
flag_in_pipe = Pipe()
zone_detection_in_pipe = Pipe()
object_retail=Pipeline()
dict=None
@app.route('/live_stock_feed')
def live_stock_feed():
    return Response(object_retail.gen_analysis(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/live_tracking_feed')
def live_tracking_feed():
    return Response(object_retail.gen_tracking(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/roi_points',methods=["POST"])
def roi_points():
    global dict
    dict=request.get_json()
    with open(file_path.get()+'/demo_zones_1.csv', 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerow(['Z1',int(dict['point_set_1'][0][0]),int(dict['point_set_1'][0][1]),
                         int(dict['point_set_1'][1][0]), int(dict['point_set_1'][1][1]),
                         int(dict['point_set_1'][2][0]), int(dict['point_set_1'][2][1]),
                         int(dict['point_set_1'][3][0]), int(dict['point_set_1'][3][1])])
    print("points")
    return "ok"
    # return Response(object_retail.gen_analysis(dict),
    #                 mimetype='multipart/x-mixed-replace; boundary=frame')

    # object_retail.gen_analysis(dict)
    # return Response("<h1>OK</h1>",
    #                 mimetype='text/html')

@app.route('/live_age_feed')
def live_age_feed():
    return Response(object_retail.gen_age_api(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def run(session_runner):
    # object_retail.use_session_runner(session_runner)
    app.run(host='0.0.0.0', debug=True, use_reloader=False,threaded=True)

