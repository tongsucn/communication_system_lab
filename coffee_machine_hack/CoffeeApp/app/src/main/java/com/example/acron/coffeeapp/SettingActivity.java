package com.example.acron.coffeeapp;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.preference.Preference;
import android.preference.PreferenceActivity;
import android.preference.PreferenceFragment;
import android.preference.PreferenceManager;
import android.widget.Toast;


/**
 * Created by acron on 02.03.2016.
 */
public class SettingActivity extends PreferenceActivity implements Preference.OnPreferenceChangeListener{

    @Override
    public void onCreate(Bundle savedInstanceState){
        super.onCreate(savedInstanceState);
        getFragmentManager().beginTransaction().replace(android.R.id.content, new MyPreferenceFragment()).commit();

    }
    public static class MyPreferenceFragment extends PreferenceFragment {
        @Override
        public void onCreate(final Bundle savedInstanceState){
            super.onCreate(savedInstanceState);
            addPreferencesFromResource(R.xml.preferences);
        }
    }

    @Override
    public boolean onPreferenceChange(Preference preference, Object value){
        return false;
    }
}
