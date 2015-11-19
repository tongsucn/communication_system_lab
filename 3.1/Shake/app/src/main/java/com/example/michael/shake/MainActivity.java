package com.example.michael.shake;

import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentActivity;
import android.support.v4.view.ViewPager;
import android.widget.LinearLayout;
import android.widget.Toast;

import java.util.ArrayList;

/**
 * GUI class. Handles all events.
 */
public class MainActivity extends FragmentActivity implements SensorEventListener {
    // Manage sensors.
    private SensorManager mSensorManager;
    private Sensor mAccelerometer;          // Accelerometer.
    private Sensor mGyroscope;              // Gyroscope.
    private Sensor mMagnetometer;           // Magnetometer.
    private Sensor mBarometer;              // Barometer.

    // Stores initial values for accelerometer.
    private float[] calibrationReference;

    private enum ShakeDirection { zero, xPos, xNeg, yPos, yNeg, zPos, zNeg }
    private ShakeDirection shakeDirection = ShakeDirection.zero;

    // Current page.
    private enum Page { Accelerometer, Gyroscope, Magnetometer, Barometer }
    private Page currentPage = Page.Accelerometer;

    // Store the number of nodes which should be displayed in the graph.
    private final int NUMBER_OF_NODES = 50;
    // Store the last time, when the sensor was called.
    private long lastDrawCallTimestamp;
    // Store last data for graphs.
    private ArrayList<float[]> gyroscopeNodes;
    private ArrayList<float[]> magnetometerNodes;
    private ArrayList<float[]> barometerNodes;
    private ArrayList<float[]> accelerometerNodes;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        ViewPager pager = (ViewPager) findViewById(R.id.viewPager);
        pager.setAdapter(new MyPagerAdapter(getSupportFragmentManager()));

        // Create sensor manager.
        this.mSensorManager = (SensorManager)getSystemService(SENSOR_SERVICE);
        // Instantiate sensors.
        this.mAccelerometer = this.mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        this.mGyroscope = this.mSensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
        this.mMagnetometer = this.mSensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);
        this.mBarometer = this.mSensorManager.getDefaultSensor(Sensor.TYPE_PRESSURE);

        // Initialize lists.
        this.gyroscopeNodes = new ArrayList<>();
        this.magnetometerNodes = new ArrayList<>();
        this.barometerNodes = new ArrayList<>();
        this.accelerometerNodes = new ArrayList<>();

        // Listen to when the user changes the page of the pageViewer.
        pager.addOnPageChangeListener(new ViewPager.OnPageChangeListener() {
            @Override
            public void onPageScrolled(int position, float positionOffset, int positionOffsetPixels) {
                // Doesn't matter.
            }

            @Override
            public void onPageSelected(int position) {
                onPageChanged(position);
            }

            @Override
            public void onPageScrollStateChanged(int state) {
                // Doesn't matter.
            }
        });
    }

    /**
     * Resume sensors.
     */
    protected void onResume() {
        super.onResume();

        switch (this.currentPage) {

            case Accelerometer:
                this.mSensorManager.registerListener(this, this.mAccelerometer, SensorManager.SENSOR_DELAY_UI);
                break;

            case Gyroscope:
                this.mSensorManager.registerListener(this, this.mGyroscope, SensorManager.SENSOR_DELAY_UI);
                break;

            case Magnetometer:
                this.mSensorManager.registerListener(this, this.mMagnetometer, SensorManager.SENSOR_DELAY_UI);
                break;

            case Barometer:
                this.mSensorManager.registerListener(this, this.mBarometer, SensorManager.SENSOR_DELAY_UI);
                break;

            default:
                break;
        }
    }

    /**
     * Pause sensors.
     */
    protected void onPause() {
        super.onPause();

        this.mSensorManager.unregisterListener(this);
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        // Just continue if the last event is more than REFRESH_TIME_MS old.
        final int REFRESH_TIME_MS = 17;
        if (System.currentTimeMillis() - this.lastDrawCallTimestamp > REFRESH_TIME_MS) {
            this.lastDrawCallTimestamp = System.currentTimeMillis();
        }
        else {
            return;
        }

        switch (event.sensor.getType()) {

            case Sensor.TYPE_ACCELEROMETER:
                this.readAccelerometer(event.values);
                break;

            case Sensor.TYPE_GYROSCOPE:
                this.readGyroscope(event.values);
                break;

            case Sensor.TYPE_MAGNETIC_FIELD:
                this.readMagnetometer(event.values);
                break;

            case Sensor.TYPE_PRESSURE:
                this.readBarometer(event.values);
                break;

            default:
                break;
        }

    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        // Not needed up to now...
    }

    /**
     * Happens when a page of the pageViewer changes.
     * @param position the position of the page in the pageViewer.
     */
    private void onPageChanged(int position) {
        // Check which page I am scrolling to.
        switch (position) {

            // Accelerometer page.
            case 0:
                this.currentPage = Page.Accelerometer;
                this.mSensorManager.unregisterListener(this);
                this.mSensorManager.registerListener(this, this.mAccelerometer, SensorManager.SENSOR_DELAY_UI);
                break;

            // Gyroscope page.
            case 1:
                this.currentPage = Page.Gyroscope;
                this.mSensorManager.unregisterListener(this);
                this.mSensorManager.registerListener(this, this.mGyroscope, SensorManager.SENSOR_DELAY_UI);
                break;

            // Magnetometer page.
            case 2:
                this.currentPage = Page.Magnetometer;
                this.mSensorManager.unregisterListener(this);
                this.mSensorManager.registerListener(this, this.mMagnetometer, SensorManager.SENSOR_DELAY_UI);
                break;

            // Barometer page.
            case 3:
                this.currentPage = Page.Barometer;
                this.mSensorManager.unregisterListener(this);
                this.mSensorManager.registerListener(this, this.mBarometer, SensorManager.SENSOR_DELAY_UI);
                break;

            // Never happens.
            default:
                break;
        }
    }

    /**
     * Return the fragment with the corresponding number out of the viewPage.
     * @param itemNumber the number corresponding to a fragment
     * @return Fragment corresponding to the itemNumber
     */
    private Fragment getFragmentFromMyPageAdapter(int itemNumber) {
        ViewPager pager = (ViewPager) findViewById(R.id.viewPager);
        MyPagerAdapter myPagerAdapter = (MyPagerAdapter) pager.getAdapter();

        return myPagerAdapter.getItem(itemNumber);
    }

    /**
     * Read the values of the accelerometer.
     * @param values contains values for x, y and z.
     */
    private void readAccelerometer(float[] values) {
        AccelerometerFragment af = (AccelerometerFragment) this.getFragmentFromMyPageAdapter(4);
        LinearLayout llAccelerometerCanvas = (LinearLayout)findViewById(R.id.llAccelerometerCanvas);

        // Add values to list.
        float[] v = this.calibrateAccelerometer(values);
        this.accelerometerNodes.add(new float[]{v[0], v[1], v[2]});
        // If there are too many values, remove the oldest.
        if (this.accelerometerNodes.size() > this.NUMBER_OF_NODES)
            this.accelerometerNodes.remove(0);

        // Send values to AccelerometerFragment.
        af.setSensorValues(this.accelerometerNodes, llAccelerometerCanvas, getApplicationContext().getResources());
        // Check if phone has been shaken.
        this.shaken(this.calibrateAccelerometer(values));
    }

    /**
     * Calibrate the accelerometer.
     * @param values values received from accelerometer.
     * @return calibrated values.
     */
    private float[] calibrateAccelerometer(float[] values) {
        if (this.calibrationReference == null) {
            this.calibrationReference = new float[3];
            this.calibrationReference[0] = values[0];
            this.calibrationReference[1] = values[1];
            this.calibrationReference[2] = values[2];
        }
        else
        {
            values[0] -= this.calibrationReference[0];
            values[1] -= this.calibrationReference[1];
            values[2] -= this.calibrationReference[2];
        }

        return values;
    }

    /**
     * Check if phone has been shaken.
     * @param values Current sensor data from accelerometer.
     * @return true if phone has been shaken.
     */
    private Boolean shaken(float[] values) {
        // This works as follows:
        // If the phone gets driven in a specific direction and the drive is stronger than the threshold,
        // store the direction. If the phone gets driven in the opposite direction, then shake happens!

        final float SHAKE_THRESHOLD = 4;
        if (values[0] > SHAKE_THRESHOLD && this.shakeDirection == ShakeDirection.xNeg
                || values[0] < -SHAKE_THRESHOLD && this.shakeDirection == ShakeDirection.xPos
                || values[1] > SHAKE_THRESHOLD && this.shakeDirection == ShakeDirection.yNeg
                || values[1] < -SHAKE_THRESHOLD && this.shakeDirection == ShakeDirection.yPos
                || values[2] > SHAKE_THRESHOLD && this.shakeDirection == ShakeDirection.zNeg
                || values[2] < -SHAKE_THRESHOLD && this.shakeDirection == ShakeDirection.zPos) {
            this.shakeDirection = ShakeDirection.zero;
            Toast.makeText(MainActivity.this, "SHAKE", Toast.LENGTH_SHORT).show();
            return true;
        }
        else if (values[0] > SHAKE_THRESHOLD) {
            this.shakeDirection = ShakeDirection.xPos;
            return false;
        }
        else if (values[0] < -SHAKE_THRESHOLD) {
            this.shakeDirection = ShakeDirection.xNeg;
            return false;
        }
        else if (values[1] > SHAKE_THRESHOLD) {
            this.shakeDirection = ShakeDirection.yPos;
            return false;
        }
        else if (values[1] < -SHAKE_THRESHOLD) {
            this.shakeDirection = ShakeDirection.yNeg;
            return false;
        }
        else if (values[2] > SHAKE_THRESHOLD) {
            this.shakeDirection = ShakeDirection.zPos;
            return false;
        }
        else if (values[2] < -SHAKE_THRESHOLD) {
            this.shakeDirection = ShakeDirection.zNeg;
            return false;
        }

        return false;
    }


    /**
     * Read the values of the gyroscope.
     * @param values values received from gyroscope.
     */
    private void readGyroscope(float[] values) {
        GyroscopeFragment gf = (GyroscopeFragment) this.getFragmentFromMyPageAdapter(1);
        LinearLayout llGyroscopeCanvas = (LinearLayout)findViewById(R.id.llGyroscopeCanvas);

        // Add values to list.
        this.gyroscopeNodes.add(new float[] {values[0], values[1], values[2]});
        // If there are too many values, remove the oldest.
        if (this.gyroscopeNodes.size() > this.NUMBER_OF_NODES)
            this.gyroscopeNodes.remove(0);

        // Send values to GyroscopeFragment.
        gf.setSensorValues(this.gyroscopeNodes, llGyroscopeCanvas, getApplicationContext().getResources());
    }


    /**
     * Read the values of the magnetometer.
     * @param values values received from magnetometer.
     */
    private void readMagnetometer(float[] values) {
        MagnetometerFragment mf = (MagnetometerFragment)this.getFragmentFromMyPageAdapter(2);
        LinearLayout llMagnetometerCanvas = (LinearLayout)findViewById(R.id.llMagnetometerCanvas);

        // Add values to list.
        this.magnetometerNodes.add(new float[] {values[0], values[1], values[2]});
        // If there are too many values, remove the oldest.
        if (this.magnetometerNodes.size() > this.NUMBER_OF_NODES)
            this.magnetometerNodes.remove(0);

        // Send values to MagnetometerFragment.
        mf.setSensorValues(this.magnetometerNodes, llMagnetometerCanvas, getApplicationContext().getResources());
    }

    /**
     * Read the values from barometer.
     * @param values values received from barometer.
     */
    private void readBarometer(float[] values) {
        BarometerFragment bf = (BarometerFragment)this.getFragmentFromMyPageAdapter(3);
        LinearLayout llBarometerCanvas = (LinearLayout)findViewById(R.id.llBarometerCanvas);

        // Add values to list.
        this.barometerNodes.add(new float[] {values[0], values[1], values[2]});
        // If there are too many values, remove the oldest.
        if (this.barometerNodes.size() > this.NUMBER_OF_NODES)
            this.barometerNodes.remove(0);

        // Send values to BarometerFragment.
        bf.setSensorValues(this.barometerNodes, llBarometerCanvas, getApplicationContext().getResources());
    }
}
