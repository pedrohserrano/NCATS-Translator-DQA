"""Wrapper for calling RDFUnit
"""
import os
import sys
import subprocess


class RDFUnitWrapper:
    __rdfunit_output_extension = '.shaclFullTestCaseResult.ttl'

    def __init__(self, path_rdfunit, verbose=False):
        """Constructor

        :param path_rdfunit: Absolute path to the RDFUnit base directory (one folder above bin)
        :param verbose: True if you want to print status messages
        """
        self.path_rdfunit = path_rdfunit
        self.__bin_rdfunit = os.path.join(self.path_rdfunit, 'bin/rdfunit')
        self.__bin_dqvreport = os.path.join(self.path_rdfunit, 'bin/dqv-report')
        self.verbose = verbose

    def rdfunit(self, file_dataset):
        """Calls rdfunit on the given dataset

        :param file_dataset: Absolute path to the dataset file (i.e., the -d parameter to rdfunit)
        :return: Path of the output file generated by rdfunit
        """
        if self.verbose:
            print('Running rdfunit on ' + file_dataset)

        # Run rdfunit
        cp = subprocess.run([self.__bin_rdfunit, '-d', file_dataset, '-r', 'shacl', '-o', 'html,turtle'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='UTF-8', cwd=self.path_rdfunit)

        # Check the return code for errors
        if cp.returncode != 0:
            sys.stderr.write('There was an error running rdfunit\n')
            sys.stderr.write(cp.stderr)
            raise Exception('rdfunit error')

        # Build the expected filename of the output file written by rdfunit
        filename_dataset_sanitized = file_dataset.replace(os.sep, '_')
        file_rdf_output = os.path.join(self.path_rdfunit, 'data', 'results',
                                       filename_dataset_sanitized + RDFUnitWrapper.__rdfunit_output_extension)

        # Check that the output file was created
        if not os.path.exists(file_rdf_output):
            # Try to extract the output file name from the output log (rdfunit writes output to stderr)
            output_line = cp.stderr.split('\n')[-2]
            file_rdf_output = output_line.split(' ')[-1]
            file_rdf_output = file_rdf_output.replace('*', 'ttl')
            file_rdf_output = os.path.join(self.path_rdfunit, file_rdf_output)

            # Check if this output file exists
            if not os.path.exists(file_rdf_output):
                sys.stderr.write('Could not find the output RDF file from rdfunit\n')
                raise FileNotFoundError(file_rdf_output)

        # Return the path to the rdfunit output file
        return file_rdf_output

    def dqv_report(self, file_rdf_output):
        """Calls dqv-report on the given file

        :param file_rdf_output: The output file from rdfunit to use as input to dqv-report (i.e., the -i parameter)
        :return: Path to the output file generated by dqv-report
        """
        if self.verbose:
            print('Running dqv-report on ' + file_rdf_output)

        # Generate an output filename for the dqv report
        filename_dqv_report = os.path.split(file_rdf_output)[1] + '.dqv_report.ttl'

        # Run dqv-report
        cp = subprocess.run([self.__bin_dqvreport, '-i', file_rdf_output, '-o', filename_dqv_report],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='UTF-8', cwd=self.path_rdfunit)

        # Check the return code for errors
        if cp.returncode != 0:
            sys.stderr.write('There was an error running dqv-report\n')
            sys.stderr.write(cp.stderr)
            raise Exception('dqv-report error')

        # Check that the dqv report file was created
        file_dqv_report = os.path.join(self.path_rdfunit, 'data', 'results', filename_dqv_report)
        if not os.path.exists(file_dqv_report):
            sys.stderr.write('Could not find the dqv-report generated file: ' + file_dqv_report + '\n')
            raise FileNotFoundError(file_dqv_report)

        # Return the path to the dqv report file
        return file_dqv_report
