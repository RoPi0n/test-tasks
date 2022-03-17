package org.test;

import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;

interface Job {
    void work();
    int priority();
}

interface Scheduler {
    List<Job> completed();
    void waitAll();
    void schedule(Job j);
    void scheduleMany(Job... jobs);
    void dispose();
}

public class SchedulerImpl implements Scheduler, Runnable {
    private class WorkerRunnable implements Runnable {
        protected Job job;

        public WorkerRunnable(Job J) {
            this.job = J;
        }

        @Override
        public void run() {
            this.job.work();
        }
    }

    public static int TOTAL_WORKERS_COUNT = 50;
    public AtomicBoolean stopped;

    private Queue<Job> jobs_queue;
    private List<Job> jobs;
    private List<Thread> threads;
    private Thread worker;

    @Override
    public void dispose() {
        this.stopped.set(true);
        this.waitAll();
    }

    @Override
    public void waitAll() {
        boolean need_check = true;

        while(need_check) {
            synchronized (this.threads) {
                for (Thread T : this.threads) {
                    try {
                        T.join();
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }

            synchronized (this.jobs_queue) {
                need_check = this.jobs_queue.size() > 0;
            }

            if (need_check) {
                try {
                    Thread.sleep(10);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    public SchedulerImpl() {
        this.jobs_queue = new LinkedList<>();
        this.jobs = new ArrayList<Job>();
        this.threads = new ArrayList<Thread>();
        this.stopped = new AtomicBoolean(false);
        this.worker = new Thread(this);
        this.worker.start();
    }

    @Override
    public synchronized void schedule(Job j) {
        this.jobs.add(j);
        this.jobs_queue.add(j);
    }

    @Override
    public synchronized List<Job> completed() {
        return new ArrayList<>(this.jobs);
    }

    @Override
    public void scheduleMany(Job... jobs) {
        ArrayList<Job> jobs_list = new ArrayList<Job>(Arrays.asList(jobs));
        Collections.sort(
                jobs_list, (l, r) -> (l.priority() < r.priority() ? -1 : (l.priority() < r.priority()) ? 1 : 0)
        );

        for (Job job : jobs_list) {
            this.schedule(job);
        }
    }

    private synchronized boolean Tick() {
        boolean R = false;

        if (this.threads.size() < TOTAL_WORKERS_COUNT) {
            Job J = null;
            synchronized (this.jobs_queue) {
                if (this.jobs_queue.size() > 0) {
                    J = this.jobs_queue.poll();
                }
            }

            if (J != null) {
                Thread T = new Thread(new WorkerRunnable(J));
                this.threads.add(T);
                T.start();
                R = true;
            }
        }

        this.threads = this.threads.stream().filter(T -> T.isAlive()).collect(Collectors.toList());

        return R;
    }

    @Override
    public void run() {
        while (!stopped.get()) {
            if (!this.Tick()) {
                try {
                    Thread.sleep(10);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }
}