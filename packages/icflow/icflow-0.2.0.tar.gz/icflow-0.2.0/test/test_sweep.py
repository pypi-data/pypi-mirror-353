#!/usr/bin/env python3

import shutil

from iccore.test_utils import get_test_data_dir, get_test_output_dir
import ictasks.task
from ictasks.task import Task

import icflow
import icflow.sweep
import icflow.sweep.reporter


def test_parameter_sweep():
    work_dir = get_test_output_dir()
    data_dir = get_test_data_dir()

    config_path = data_dir / "parameter_sweep_example.yaml"
    config = icflow.sweep.config.read(config_path)
    changed_program = config.program.replace("<full_path>", str(data_dir))

    run_config = icflow.sweep.config.SweepConfig(
        title=config.title,
        program=changed_program,
        parameters=config.parameters,
    )

    sweep_dir = icflow.sweep.run(run_config, work_dir, config_path)
    result_dir = sweep_dir / "tasks"

    tasks = ictasks.task.read_all(result_dir)
    for task in tasks:
        assert task.finished and task.return_code == 0
    assert len(tasks) == 4

    icflow.sweep.reporter.monitor_plot(sweep_dir)

    shutil.rmtree(work_dir)


def test_linked_parameter_sweep():
    work_dir = get_test_output_dir()
    data_dir = get_test_data_dir()

    config_path = data_dir / "linked_parameter_sweep_example.yaml"
    config = icflow.sweep.config.read(config_path)
    changed_program = config.program.replace("<full_path>", str(data_dir))

    run_config = icflow.sweep.config.SweepConfig(
        title=config.title,
        program=changed_program,
        parameters=config.parameters,
        linked_parameters=config.linked_parameters,
    )

    sweep_dir = icflow.sweep.run(run_config, work_dir, config_path)
    result_dir = sweep_dir / "tasks"

    tasks = ictasks.task.read_all(result_dir)
    for task in tasks:
        assert task.finished and task.return_code == 0
    assert len(tasks) == 4

    shutil.rmtree(work_dir)


def test_parameter_sweep_reporter():

    tasks = [
        Task(
            id="complete_task",
            launch_cmd="python3 fake.py --complete",
            state="finished",
            pid=21,
        ),
        Task(
            id="incomplete_task",
            launch_cmd="python3 fake.py --incomplete",
            state="created",
            pid=22,
        ),
    ]

    task_str = ictasks.task.tasks_to_str(
        [t for t in tasks if t.finished], ["id", "launch_cmd", "pid"]
    )

    assert "id: complete_task" in task_str
    assert "id: incomplete_task" not in task_str
    assert "launch_cmd: python3 fake.py --complete" in task_str
    assert "launch_cmd: python3 fake.py --incomplete" not in task_str
    assert "pid: 21" in task_str
    assert "pid: 22" not in task_str
