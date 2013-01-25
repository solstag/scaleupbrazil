#!/usr/bin/env python
"""
command-line utility which takes staged scans,
creates jobs for them, and then starts those jobs.
spends money!
"""

import sys
import os
import logging
import logging.config

import secondEntry as se

def main():

	router = se.Router()

	logger.info('creating jobs')
	new_jobs = router.create_jobs()

	logger.info('starting jobs')
	router.start_jobs()

if __name__ == "__main__":

	logger = se.config.start_log()

	main()
