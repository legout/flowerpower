from test_job import TestJob

def main():
    test_job = TestJob("job1")
    test_job.add_job(1, 2, 3, a="A")

if __name__ == "__main__":
    main()