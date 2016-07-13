# coding=utf-8
import luigi


class ExtractFrames(luigi.Task):
    video_file_name = luigi.Parameter(default="input.mp4")

    def requires(self):
        return []

    def output(self):
        # not necessary i think
        # call functions
        return luigi.LocalTarget('test.txt')

    def run(self):
        return 1


class IdentifyCursor(luigi.Task):
    def requires(self):
        return [ExtractFrames()]

    def output(self):
        return luigi.LocalTarget('test.txt')

    def run(self):
        return 1


class ExtractAudio(luigi.Task):
    def requires(self):
        return []

    def output(self):
        return luigi.LocalTarget('test.txt')

    def run(self):
        return 1


class ExtractVideoDetails(luigi.Task):
    def requires(self):
        return []

    def output(self):
        return luigi.LocalTarget('test.txt')

    def run(self):
        return 1


class GetVttFiles(luigi.Task):
    def requires(self):
        return []

    def output(self):
        return luigi.LocalTarget('test.txt')

    def run(self):
        return 1


if __name__ == '__main__':
    luigi.run(["--local-scheduler"], main_task_cls=IdentifyCursor)
