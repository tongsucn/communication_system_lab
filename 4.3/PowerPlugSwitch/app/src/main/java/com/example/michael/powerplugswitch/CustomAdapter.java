package com.example.michael.powerplugswitch;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Switch;
import android.widget.TextView;

/**
 * CustomAdapter. Fill a listView with custom-layout-items.
 * Basic example from: http://techlovejump.com/android-listview-with-checkbox/
 */
class CustomAdapter extends ArrayAdapter<Plug> {
    private Plug[] plugItems = null;
    private final Context context;

    public CustomAdapter(Context context, Plug[] plugItems) {
        super(context, R.layout.row, plugItems);

        this.context = context;
        this.plugItems = plugItems;
    }

    @SuppressLint("ViewHolder") // we don't expect many updates or too many items in listView, so it can be ignored.
    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        LayoutInflater inflater = ((Activity) context).getLayoutInflater();
        convertView = inflater.inflate(R.layout.row, parent, false);

        TextView textViewPlug = (TextView) convertView.findViewById(R.id.textViewPlug);
        Switch switchPlug = (Switch) convertView.findViewById(R.id.switchPlug);

        textViewPlug.setText(this.plugItems[position].getDescription());
        switchPlug.setChecked(this.plugItems[position].getState());
        switchPlug.setText(this.plugItems[position].getId());

        return convertView;
    }
}
