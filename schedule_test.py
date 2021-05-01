# import schedule
# import time

# import datetime
# from traceback import format_exc

# from schedule import Job, Scheduler


# class SafeScheduler(Scheduler):
#     """
#     An implementation of Scheduler that catches jobs that fail, logs their
#     exception tracebacks as errors, and keeps going.

#     Use this to run jobs that may or may not crash without worrying about
#     whether other jobs will run or if they'll crash the entire script.
#     """

#     def __init__(self, rerun_immediately=True):
#         self.rerun_immediately = rerun_immediately

#         super().__init__()

#     # def _run_job(self, job: Job):
#     #     try:
#     #         super()._run_job(job)
#     #     except Exception:  # pylint: disable=broad-except
#     #         print(next(iter(job.tags)))

#     #         # self.logger.error(f"Error while {next(iter(job.tags))}...\n{format_exc()}")
#     #         job.last_run = datetime.datetime.now()
#     #         if not self.rerun_immediately:
#     #             # Reschedule the job for the next time it was meant to run, instead of
#     #             # letting it run
#     #             # next tick
#     #             job._schedule_next_run()  # pylint: disable=protected-access

# def job10s():
#     print("I'm working...10s")

# def job10m():
#     print("I'm working...10m")


# schedule = SafeScheduler()

# schedule.every(10).seconds.do(job10s)
# schedule.every(10).seconds.do(job10m)
# # schedule.every().hour.do(job).tag('1hour')
# # schedule.every().day.at("10:30").do(job).tag('at 10:30')
# # schedule.every(5).to(10).minutes.do(job).tag('from 5 to 10 míns')
# # schedule.every().monday.do(job)
# # schedule.every().wednesday.at("13:15").do(job)
# # schedule.every().minute.at(":17").do(job)

# while True:
#     schedule.run_pending()
#     time.sleep(1)