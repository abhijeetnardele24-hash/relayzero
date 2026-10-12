.PHONY: run test eval build clean

# Root Makefile delegating to official track_2b challenge directory
run:
	@echo "Launching RelayZero from root..."
	$(MAKE) -C track_2b run

test:
	@echo "Running tests from root..."
	$(MAKE) -C track_2b test

eval:
	@echo "Running evaluation benchmark from root..."
	$(MAKE) -C track_2b eval

build:
	@echo "Building artifacts..."
	$(MAKE) -C track_2b build

clean:
	@echo "Cleaning artifacts..."
	$(MAKE) -C track_2b clean
