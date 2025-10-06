# Scraping Job Management Guide

## Overview
The scraping system now supports automatic job starting and scheduling. When you create a scraping job from the Django admin, it can automatically start immediately or be scheduled for later execution.

## Features

### 1. Automatic Job Starting
- **Auto Start**: When enabled, jobs automatically start when created
- **Immediate Execution**: Jobs without scheduling start immediately
- **Scheduled Execution**: Jobs with future scheduling times are queued for later

### 2. Job Scheduling
- **Scheduled At**: Set a specific date and time for job execution
- **Flexible Timing**: Schedule jobs for any future time
- **Status Tracking**: Jobs show as "scheduled" until execution time

### 3. Admin Interface Enhancements
- **Action Buttons**: Start/Cancel buttons for each job
- **Bulk Actions**: Start or cancel multiple jobs at once
- **Status Monitoring**: Real-time status updates
- **Progress Tracking**: See products scraped, found, and errors

## How to Use

### Creating a Scraping Job

1. **Go to Django Admin** → **Scraping** → **Scraping jobs** → **Add**

2. **Fill in Job Information**:
   - **Name**: Descriptive name for the job
   - **Website**: Select the website to scrape
   - **Product List**: Choose products to search for
   - **Marketplace**: Select the marketplace type
   - **Created By**: Will be set to current user

3. **Configure Scheduling**:
   - **Auto Start**: ✅ Check to start automatically
   - **Scheduled At**: Leave empty for immediate start, or set future date/time

4. **Save the Job**:
   - If auto-start is enabled and no scheduling: Job starts immediately
   - If auto-start is enabled with future scheduling: Job is scheduled
   - If auto-start is disabled: Job remains in "pending" status

### Managing Jobs

#### Individual Job Actions
- **Start Button**: Appears for pending/scheduled jobs
- **Cancel Button**: Appears for running jobs
- **Status Updates**: Real-time status changes

#### Bulk Actions
1. Select multiple jobs from the list
2. Choose action from dropdown:
   - "Start selected scraping jobs"
   - "Cancel selected scraping jobs"
3. Click "Go"

### Job Statuses

- **Pending**: Job created but not started
- **Scheduled**: Job scheduled for future execution
- **Running**: Job currently executing
- **Completed**: Job finished successfully
- **Failed**: Job encountered an error
- **Cancelled**: Job was cancelled by user

### Monitoring Progress

- **Products Scraped**: Number of products successfully scraped
- **Products Found**: Total products found during search
- **Errors Count**: Number of errors encountered
- **Task ID**: Celery task identifier for monitoring

## Example Workflows

### Immediate Scraping
1. Create job with auto-start enabled
2. Leave scheduled_at empty
3. Job starts immediately upon saving

### Scheduled Scraping
1. Create job with auto-start enabled
2. Set scheduled_at to future time (e.g., tomorrow 9:00 AM)
3. Job status becomes "scheduled"
4. Job automatically starts at scheduled time

### Manual Control
1. Create job with auto-start disabled
2. Job remains in "pending" status
3. Use "Start" button when ready to begin

## Troubleshooting

### Job Not Starting
- Check if Celery worker is running
- Verify Redis connection
- Check job status and error messages
- Ensure website and product list are properly configured

### Scheduling Issues
- Verify scheduled time is in the future
- Check system timezone settings
- Monitor Celery logs for scheduling errors

### Performance Tips
- Use appropriate rate limiting for websites
- Monitor system resources during large jobs
- Consider splitting large product lists into smaller jobs

## Technical Details

### Celery Integration
- Jobs use Celery for asynchronous execution
- Redis as message broker
- Task IDs stored for monitoring and cancellation

### Database Changes
- Added `scheduled_at` field for scheduling
- Added `auto_start` field for automatic execution
- Added `scheduled` status for queued jobs

### Admin Enhancements
- Custom admin actions for job management
- Real-time status updates
- Bulk operations support
- Enhanced filtering and search

## API Endpoints

The system also provides REST API endpoints for programmatic access:

- `GET /api/scraping/jobs/` - List all jobs
- `POST /api/scraping/jobs/` - Create new job
- `GET /api/scraping/jobs/{id}/` - Get job details
- `PATCH /api/scraping/jobs/{id}/` - Update job status
- `POST /api/scraping/trigger/` - Trigger scraping manually

## Next Steps

1. **Test the System**: Create a test job to verify functionality
2. **Configure Websites**: Set up scraping configurations for your target websites
3. **Create Product Lists**: Define products you want to monitor
4. **Schedule Regular Jobs**: Set up recurring scraping for price monitoring
5. **Monitor Results**: Check scraped products and violations

## Support

If you encounter issues:
1. Check Celery worker status
2. Review job error messages
3. Verify website configurations
4. Check system logs for detailed error information
