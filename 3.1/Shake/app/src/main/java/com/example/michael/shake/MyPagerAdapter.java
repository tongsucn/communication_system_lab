package com.example.michael.shake;

import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentPagerAdapter;

/**
 * Class to show show several pages with different fragment content.
 * With much help from:
 * http://stackoverflow.com/questions/18413309/how-to-implement-a-viewpager-with-different-fragments-layouts
 */
class MyPagerAdapter extends FragmentPagerAdapter {

    /**
     * Constructor.
     * @param fm fragmentManager
     */
    public MyPagerAdapter(FragmentManager fm) {
        super(fm);
    }

    /**
     * Get a specific fragment from the viewPager.
     * @param pos The position of the fragment in the viewPager.
     * @return Fragment of the viewPager.
     */
    @Override
    public Fragment getItem(int pos) {
        switch(pos) {

            case 0:
                return AccelerometerFragment.newInstance("Accelerometer");

            case 1:
                return GyroscopeFragment.newInstance();

            case 2:
                return MagnetometerFragment.newInstance();

            case 3:
                return BarometerFragment.newInstance();

            default:
                return AccelerometerFragment.newInstance("Default");
        }
    }

    /**
     * Returns the number of the viewPage pages.
     * @return number of viewPage pages.
     */
    @Override
    public int getCount() {
        return 4;
    }
}
