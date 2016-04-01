package com.example.acron.coffeeapp;

import android.support.design.widget.Snackbar;
import android.view.View;
import android.widget.Button;
import android.widget.ToggleButton;

/**
 * Created by acron on 16.02.2016.
 */
public class ProductButtonListener implements Button.OnClickListener {


    public void onClick(View v) {
        int id = v.getId();
        ToggleButton tB;
        if (v instanceof ToggleButton) {
            tB = (ToggleButton) v;
        } else {
            return;
        }
        Snackbar.make(v, "Counted "+tB.getText(), Snackbar.LENGTH_LONG).setAction("Action", null).show();

        tB.setClickable(false);
       switch(id){
           case R.id.btnProd1:{
               Boolean res = Communication.requestProduct(1);
               Snackbar.make(v,"Status: " + res + " Address: "+Communication.getServerAddress(), Snackbar.LENGTH_LONG).setAction("Action", null).show();
               break;
           }
           case R.id.btnProd2:{
               Communication.requestProduct(2);
               break;
           }
           case R.id.btnProd3:{
               Communication.requestProduct(3);
               break;
           }
           case R.id.btnProd4:{
               Communication.requestProduct(4);
               break;
           }
           case R.id.btnProd5:{
               Communication.requestProduct(5);
               break;
           }
           case R.id.btnProd6:{
               Communication.requestProduct(6);
               break;
           }
           default:{
               break;
           }
       }
        tB.setChecked(false);
        tB.setClickable(true);
    }


}

