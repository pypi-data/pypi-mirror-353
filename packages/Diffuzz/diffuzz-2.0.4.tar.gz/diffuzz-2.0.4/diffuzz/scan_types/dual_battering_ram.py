from httpdiff import Baseline, Response
from httpinsert.location import Location

from threading import Thread, BoundedSemaphore, Lock
import random
import time
import string

import sys

from urllib.parse import urlunparse, quote,urlparse, unquote

class DualBatteringRam: 
    def __init__(self, options, custom_blob=None):
        self.custom_blob=custom_blob
        self.stop=False
        self.options=options
        self.baseline = None
        self.job_lock = BoundedSemaphore(self.options.args.threads)
        self.calibration_lock = Lock()
        self.calibrating = False


    def calibrate_baseline(self,insertion_point):
        baseline = self.baseline or  Baseline(custom_blob=self.custom_blob)
        baseline.verbose = self.options.args.verbose
        baseline.analyze_all = not self.options.args.no_analyze_all
        self.options.logger.verbose("Calibration baseline")

        sleep_time = self.options.args.calibration_sleep/1000 or self.options.args.sleep/1000
        payload= ''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(10,20))) # Generating in case num_calibrations is 0
        for i in range(self.options.args.num_calibrations):
            payload= ''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(10,20)))
            time.sleep(sleep_time)
            resp,response_time,error,_= self.send(insertion_point,payload)
            if error and self.options.args.ignore_errors is False:
                self.stop=True
                self.options.logger.critical(f"Error occurred during calibration, stopping scan as ignore-errors is not set - {error}")
                return None
            baseline.add_response(resp,response_time,error,payload)

        time.sleep(sleep_time)
        resp, response_time, error,_= self.send(insertion_point,payload)
        if error and self.options.args.ignore_errors is False:
            self.stop=True
            self.options.logger.critical(f"Error occurred during calibration, stopping scan as ignore-errors is not set - {error}")
            return None
        baseline.add_response(resp,response_time,error,payload)
        self.options.logger.verbose("Done calibrating")
        return baseline



    def send(self,insertion_points,payload):
        time.sleep(self.options.args.sleep/1000)
        insertions = []
        for insertion_point in insertion_points:
            insertion = insertion_point.insert(payload,self.options.req,format_payload=True,default_encoding=not self.options.args.disable_encoding)
            insertions.append(insertion)
        if self.stop is True:
            return None, 0.0, b"self.stop is True, terminating execution", insertion
        resp,response_time,error = self.options.req.send(debug=self.options.args.debug,insertions=insertions,allow_redirects=self.options.args.allow_redirects,timeout=self.options.args.timeout,verify=self.options.args.verify,proxies=self.options.proxies)
        if error:
            self.options.logger.debug(f"Error occured while sending request: {error}")
            error = str(type(error)).encode()
        resp=Response(resp)
        return resp,response_time,error,insertion



    def check_payload(self,payload1,payload2,insertion_points,url_encoded,checks=0):
        payload3 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(10,20)))

        if self.baseline is None:
            self.calibration_lock.acquire()
            if self.baseline is None:
                self.baseline =  self.calibrate_baseline(insertion_points)
            self.calibration_lock.release()
        baseline = self.baseline
        if self.stop is True:
            self.job_lock.release()
            return

        resp,response_time,error,insertion1= self.send(insertion_points,payload1)

        resp2,response_time2,error2,insertion2 = self.send(insertion_points,payload2)

        
        diffs = list(baseline.find_diffs(resp,response_time,error))
        diffs2 = list(baseline.find_diffs(resp2,response_time2,error2))

        if diffs == diffs2:
            self.job_lock.release()
            return
        resp3,response_time3,error3,_= self.send(insertion_points,payload3)

        if self.stop is True:
            self.job_lock.release()
            return

        diffs3 = list(self.baseline.find_diffs(resp3,response_time3,error3))

        sections_diffs3_len = {}
        for i in diffs3:
            if i["section"] not in sections_diffs3_len.keys():
                sections_diffs3_len[i["section"]] = 0
            sections_diffs3_len[i["section"]] += len(i["diffs"])
        for _ in diffs3:
            if self.calibrating is True:
                self.calibration_lock.acquire() # Wait for calibration to finish
                self.calibration_lock.release()
                return self.check_payload(payload1,payload2,insertion_points,url_encoded,checks=checks)
            self.calibration_lock.acquire()
            self.calibrating = True
            self.options.logger.verbose(f"Baseline changed, calibrating again - {sections_diffs3_len}")
            self.baseline = self.calibrate_baseline(insertion_points)
            self.calibration_lock.release()
            self.calibrating = False
            return self.check_payload(payload1,payload2,insertion_points,url_encoded,checks=checks)

            
        if checks >= self.options.args.num_verifications:
            sections_diffs_len = {}
            for i in diffs:
                if i["section"] not in sections_diffs_len.keys():
                    sections_diffs_len[i["section"]] = [0,0]
                sections_diffs_len[i["section"]][0] += len(i["diffs"])
            for i in diffs2:
                if i["section"] not in sections_diffs_len.keys():
                    sections_diffs_len[i["section"]] = [0,0]
                sections_diffs_len[i["section"]][1] += len(i["diffs"])

            self.options.logger.debug(f"Diffs:\n{str(diffs)}\nDiffs2:\n{str(diffs2)}\n")
            payload1 = insertion1.payload
            payload2 = insertion2.payload
            if url_encoded is True:
                payload1 = f"URLENCODED:{quote(payload1)}"
                payload2 = f"URLENCODED:{quote(payload2)}"
            self.options.logger.info(f"Found diff\nPayload1: {payload1}\nPayload2: {payload2}\ndiffs: {sections_diffs_len}\n")

        else:
            return self.check_payload(payload1,payload2,insertion_points,url_encoded,checks=checks+1)
        self.job_lock.release()


    def scan(self, insertion_points):
        with open(self.options.args.wordlist, "r") as f:
            wordlist = f.read().splitlines()

        jobs=[]
        for word in wordlist:
            url_encoded=False
            if word.startswith("URLENCODED:"):
                word = word.split("URLENCODED:")[1]
                word = unquote(word) # URL decoding
                url_encoded=True
            self.job_lock.acquire()
            payload1,payload2 = word.split("§§§§")
            if self.stop is True:
                return
            job = Thread(target=self.check_payload,args=(payload1,payload2,insertion_points,url_encoded))
            jobs.append(job)
            job.start()

        for job in jobs:
            job.join()
