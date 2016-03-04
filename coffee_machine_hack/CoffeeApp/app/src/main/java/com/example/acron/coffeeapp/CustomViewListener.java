package com.example.acron.coffeeapp;

import android.content.res.ColorStateList;
import android.graphics.Color;
import android.support.design.widget.Snackbar;
import android.view.View;

/**
 * Created by acron on 11.02.2016.
 */
public class CustomViewListener implements View.OnClickListener{
    private boolean machineStatus = false;

    public CustomViewListener(){
        super();
        machineStatus = Communication.getMachineStatus();
    }

    public void setMachineStatus(boolean status){
        machineStatus = status;
    }

    public void onClick(View view){
        if(machineStatus == false) {
            Snackbar.make(view, "Turning on", Snackbar.LENGTH_LONG).setAction("Action", null).show();
            machineStatus = Communication.setMachineStatus(true);
        }else{
            Snackbar.make(view, "Turning off", Snackbar.LENGTH_LONG).setAction("Action", null).show();
            machineStatus = Communication.setMachineStatus(false);
        }
        view.setBackgroundTintList(ColorStateList.valueOf(machineStatus?0xFF009966:0xFFB01111));
    }
}
