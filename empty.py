from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import requests
import time
import logging

app = FastAPI()

# Set up logging
logging.basicConfig(
    filename='robojar.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.post("/api/start-robojar-test")
async def start_robojar_test():
    """
    Starts a RoboJar test with the 'new' protocol and 'Artemio Test' title.
    Runs for 5 seconds then stops automatically.
    
    Returns:
        JSON response with test status and details
    """
    session = requests.Session()
    base_url = 'http://192.168.137.201/rj'
    
    try:
        logging.info("Starting RoboJar test")
        
        # Step 1: Initialize session by visiting the page
        logging.info("Initializing session...")
        session.get(f'{base_url}/basic1.php')
        time.sleep(1)
        
        # Step 2: Get protocol data
        logging.info("Fetching protocol data...")
        response = session.get(f'{base_url}/protocol_mgr.php', params={
            'func': 'printproto',
            'format': 'js'
        })
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to fetch protocols: HTTP {response.status_code}"
            )
        
        proto_data = response.json()
        logging.info(f"Found {len(proto_data)} protocols")
        
        # Step 3: Find the "new" protocol
        new_protocol = None
        for proto in proto_data:
            if proto['title'].lower() == 'new':
                new_protocol = proto
                break
        
        if not new_protocol:
            available_protocols = [p['title'] for p in proto_data]
            logging.error(f"'new' protocol not found. Available: {available_protocols}")
            raise HTTPException(
                status_code=404, 
                detail=f"'new' protocol not found. Available protocols: {', '.join(available_protocols)}"
            )
        
        logging.info(f"Selected protocol: {new_protocol['title']} (ID: {new_protocol['id']})")
        
        # Step 4: Get stage data and calculate timing
        stage_data = new_protocol['stagedata']
        total_duration = sum(stage['duration'] for stage in stage_data)
        current_time = int(time.time())
        
        start_tm = current_time
        end_tm = start_tm + total_duration
        
        logging.info(f"Total protocol duration: {total_duration} seconds")
        
        # Step 5: Create the run in database
        logging.info("Creating run in database...")
        run_params = {
            'func': 'newrun',
            'protocol_id': new_protocol['id'],
            'title': 'Artemio Test',
            'dose': '',
            'chem': '',
            'comment': 'Automated test via API',
            'start': start_tm,
            'end': end_tm
        }
        
        run_response = session.get(f'{base_url}/run_mgr.php', params=run_params)
        logging.info(f"Run creation response: {run_response.text}")
        time.sleep(1)
        
        # Step 6: Set RPM for first stage
        first_stage_rpm = stage_data[0]['rpm']
        logging.info(f"Setting RPM to {first_stage_rpm}...")
        
        rpm_response = session.get(f'{base_url}/setrpm.php', params={
            'rpm': first_stage_rpm
        })
        logging.info(f"RPM response: {rpm_response.text}")
        time.sleep(0.5)
        
        # Step 7: Set G-value for first stage
        gval = round(0.1839 * (first_stage_rpm ** 1.4227))
        logging.info(f"Setting G-value to {gval}...")
        
        gval_response = session.get(f'{base_url}/setgval.php', params={
            'gval': gval
        })
        logging.info(f"G-value response: {gval_response.text}")
        time.sleep(0.5)
        
        # Step 8: Start floc control
        logging.info("Starting floc control...")
        start_floc_response = session.get(f'{base_url}/floc_control.php', params={
            'command': 'run_floc'
        })
        
        # Parse start response
        try:
            start_data = start_floc_response.json()
            logging.info(f"Start floc response: {start_data}")
            
            # Check if start was successful (adjust condition based on actual response)
            if start_data.get('status') == 'error':
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to start floc: {start_data.get('message')}"
                )
        except ValueError:
            # Response wasn't JSON, log raw text
            logging.info(f"Start floc response (raw): {start_floc_response.text}")
            start_data = {"raw_response": start_floc_response.text}
        
        logging.info("✓ Test started successfully, waiting 5 seconds...")
        
        # Step 9: Wait 5 seconds
        time.sleep(5)
        
        # Step 10: Stop the test
        logging.info("Stopping test...")
        
        stop_floc_response = session.get(f'{base_url}/floc_control.php', params={
            'command': 'stop_floc'
        })
        
        # Parse stop response
        try:
            stop_data = stop_floc_response.json()
            logging.info(f"Stop floc response: {stop_data}")
        except ValueError:
            logging.info(f"Stop floc response (raw): {stop_floc_response.text}")
            stop_data = {"raw_response": stop_floc_response.text}
        
        # Set RPM to 0
        rpm_stop_response = session.get(f'{base_url}/setrpm.php', params={'rpm': 0})
        logging.info(f"RPM set to 0: {rpm_stop_response.text}")
        
        # Set G-value to 0
        gval_stop_response = session.get(f'{base_url}/setgval.php', params={'gval': 0})
        logging.info(f"G-value set to 0: {gval_stop_response.text}")
        
        logging.info("✓ Test completed and stopped successfully")
        
        # Return success response
        return JSONResponse({
            "status": "success",
            "message": "Test completed successfully",
            "details": {
                "protocol": new_protocol['title'],
                "protocol_id": new_protocol['id'],
                "run_title": "Artemio Test",
                "rpm": first_stage_rpm,
                "gval": gval,
                "duration_seconds": 5,
                "total_protocol_duration": total_duration,
                "start_response": start_data,
                "stop_response": stop_data
            }
        })
        
    except HTTPException as he:
        # Re-raise HTTP exceptions
        logging.error(f"HTTP Exception: {he.detail}")
        raise he
        
    except requests.exceptions.RequestException as re:
        # Network/connection errors
        logging.error(f"Network error: {str(re)}")
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to RoboJar system: {str(re)}"
        )
        
    except Exception as e:
        # Catch-all for unexpected errors
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        
        # Try emergency stop in case something went wrong
        try:
            logging.info("Attempting emergency stop...")
            session.get(f'{base_url}/floc_control.php', params={'command': 'stop_floc'})
            session.get(f'{base_url}/setrpm.php', params={'rpm': 0})
            session.get(f'{base_url}/setgval.php', params={'gval': 0})
            logging.info("Emergency stop executed")
        except:
            logging.error("Emergency stop also failed!")
        
        raise HTTPException(
            status_code=500,
            detail=f"Internal error during test: {str(e)}"
        )


@app.post("/api/emergency-stop-robojar")
async def emergency_stop_robojar():
    """
    Emergency stop for RoboJar - immediately stops all equipment
    
    Returns:
        JSON response with stop status
    """
    try:
        logging.warning("EMERGENCY STOP TRIGGERED")
        
        session = requests.Session()
        base_url = 'http://192.168.137.201/rj'
        
        # Stop floc control
        stop_response = session.get(f'{base_url}/floc_control.php', params={
            'command': 'stop_floc'
        })
        
        try:
            stop_data = stop_response.json()
            logging.info(f"Emergency stop response: {stop_data}")
        except ValueError:
            stop_data = {"raw_response": stop_response.text}
            logging.info(f"Emergency stop response (raw): {stop_response.text}")
        
        # Set RPM to 0
        session.get(f'{base_url}/setrpm.php', params={'rpm': 0})
        
        # Set G-value to 0
        session.get(f'{base_url}/setgval.php', params={'gval': 0})
        
        logging.info("Emergency stop completed")
        
        return JSONResponse({
            "status": "success",
            "message": "Emergency stop executed successfully",
            "stop_response": stop_data
        })
        
    except Exception as e:
        logging.error(f"Emergency stop failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Emergency stop failed: {str(e)}"
        )


@app.get("/api/robojar-status")
async def get_robojar_status():
    """
    Get current status of RoboJar (optional - for monitoring)
    
    Returns:
        JSON with current RPM, stage, etc.
    """
    try:
        session = requests.Session()
        base_url = 'http://192.168.137.201/rj'
        
        # You could add endpoints here to check current status
        # This would require finding the right endpoint on the RoboJar system
        
        return JSONResponse({
            "status": "success",
            "message": "Status check not yet implemented"
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get status: {str(e)}"
        )