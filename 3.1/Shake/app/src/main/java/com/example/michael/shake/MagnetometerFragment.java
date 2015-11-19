package com.example.michael.shake;

import android.content.res.Resources;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.drawable.BitmapDrawable;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.util.ArrayList;

/**
 * Created by Michael on 12.11.2015.
 * Show the magnetometer parameters.
 */
public class MagnetometerFragment extends Fragment {
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        View v = inflater.inflate(R.layout.magnetometer_frag, container, false);

        TextView tv = (TextView) v.findViewById(R.id.tvMagnetometer);
        tv.setText(getArguments().getString("msg"));

        return v;
    }

    public static MagnetometerFragment newInstance() {
        MagnetometerFragment f = new MagnetometerFragment();
        Bundle b = new Bundle();
        b.putString("msg", "Magnetometer");

        f.setArguments(b);

        return f;
    }

    /**
     * Draw the sensor values into a graph.
     * @param listOfNodes A list of sensor values
     * @param llMagnetometerCanvas LinearLayout of our canvas.
     */
    @SuppressWarnings("deprecation")
    public void setSensorValues(ArrayList<float[]> listOfNodes, LinearLayout llMagnetometerCanvas, Resources resources) {
        // Get size of layout.
        float width = llMagnetometerCanvas.getWidth();
        float height = llMagnetometerCanvas.getHeight();
        float horizontalStepSize = width / (listOfNodes.size() + 2); // +2 because we don't want to draw on left/right border.

        // Init Paint and Bitmap.
        Paint paint = new Paint();
        paint.setColor(Color.BLACK);
        paint.setAntiAlias(true);
        paint.setStrokeWidth(1f);
        paint.setTextSize(30f);
        Bitmap bg = Bitmap.createBitmap((int)width, (int)height, Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(bg);

        // Go through each node and get max for correct scaling.
        float max = 0;
        for (int i = 0; i < listOfNodes.size(); i++) {
            if (Math.abs(listOfNodes.get(i)[0]) > max)
                max = Math.abs(listOfNodes.get(i)[0]);

            if (Math.abs(listOfNodes.get(i)[1]) > max)
                max = Math.abs(listOfNodes.get(i)[1]);

            if (Math.abs(listOfNodes.get(i)[2]) > max)
                max = Math.abs(listOfNodes.get(i)[2]);
        }

        // Draw horizontal line, which depicts a zero value.
        canvas.drawLine(horizontalStepSize,
                height / 2,
                width - horizontalStepSize,
                height / 2, paint);
        canvas.drawText(String.valueOf(0), 0, height / 2 - 3, paint);

        // Draw other horizontal lines, which depict integer values.
        float stepSize = 4f;
        for (float i = stepSize; i < max; i += stepSize) {
            canvas.drawLine(horizontalStepSize,
                    height / 2 - (i / max) * (height / 2),
                    width - horizontalStepSize,
                    height / 2 - (i / max) * (height / 2),
                    paint);
            canvas.drawText(String.valueOf(Math.round(i * 100)/100.0),
                    0,
                    height / 2 - (i / max) * (height / 2) - 3,
                    paint);

            canvas.drawLine(horizontalStepSize,
                    height / 2 + (i / max) * (height / 2),
                    width - horizontalStepSize,
                    height / 2 + (i / max) * (height / 2),
                    paint);
            canvas.drawText(String.valueOf(-Math.round(i * 100)/100.0),
                    0,
                    height / 2 + (i / max) * (height / 2) - 3,
                    paint);
        }
        paint.setStrokeWidth(4f);

        // Draw graph for x values.
        paint.setColor(Color.RED);
        for (int i = 1; i < listOfNodes.size(); i++) {
            canvas.drawLine(
                    horizontalStepSize * (i),                                           // x Start.
                    (height / 2) - (listOfNodes.get(i - 1)[0] / max) * (height / 2),    // y Start.
                    horizontalStepSize * (i + 1),                                       // x End.
                    (height / 2) - (listOfNodes.get(i)[0] / max) * (height / 2),        // y End.
                    paint);
        }

        // Draw graph for y values.
        paint.setColor(Color.GREEN);
        for (int i = 1; i < listOfNodes.size(); i++) {
            canvas.drawLine(
                    horizontalStepSize * (i),                                           // x Start.
                    (height / 2) - (listOfNodes.get(i - 1)[1] / max) * (height / 2),    // y Start.
                    horizontalStepSize * (i + 1),                                       // x End.
                    (height / 2) - (listOfNodes.get(i)[1] / max) * (height / 2),        // y End.
                    paint);
        }

        // Draw graph for z values.
        paint.setColor(Color.BLUE);
        for (int i = 1; i < listOfNodes.size(); i++) {
            canvas.drawLine(
                    horizontalStepSize * (i),                                           // x Start.
                    (height / 2) - (listOfNodes.get(i - 1)[2] / max) * (height / 2),    // y Start.
                    horizontalStepSize * (i + 1),                                       // x End.
                    (height / 2) - (listOfNodes.get(i)[2] / max) * (height / 2),        // y End.
                    paint);
        }

        // Give canvas to layout.
        if(android.os.Build.VERSION.SDK_INT < android.os.Build.VERSION_CODES.JELLY_BEAN) {
            llMagnetometerCanvas.setBackgroundDrawable(new BitmapDrawable(resources, bg));
        } else {
            llMagnetometerCanvas.setBackground(new BitmapDrawable(resources, bg));
        }
    }
}
