import java.awt.*;
import java.util.Vector;

@SuppressWarnings("serial")
class BarChart extends Panel
{			   
	private int	barWidth = 20;

	private Vector<Integer>	data;
	private Vector<String>	dataLabels;
	private Vector<Color>	dataColors;

       /**
       SER515 #1: Design By Contract - what is the assumed precondition
       of the Vectors in use in the for loop? Add a check to avoid any errors.
       Design an approach to gracefully handle any errors
       */
	public void paint(Graphics g)
	{
		setSize(200,250);
		Image duke = Toolkit.getDefaultToolkit().getImage("duke2.gif");
		g.drawImage(duke, 80, 10, this);

		try {
			if (dataLabels == null || dataColors == null || data == null) {
				throw(new Exception("Missing data for one of the following fields: data, label, or color."));
			}
		} catch(Exception e) {
			System.out.println(e);
			return;
		}
		
		try {
			if (dataLabels.size() != data.size() || data.size() != dataColors.size()) {
				throw(new Exception("Data mismatch"));
			}
		} catch(Exception e) {
			System.out.println(e);
			return;
		}

			for (int i = 0; i < data.size(); i++)
			{				  
				int yposition = 100+i*barWidth;
				try {
					if (!(dataColors.elementAt(i) instanceof Color)) {
						throw(new Exception("Invalid value for type color"));
					}
				} catch(Exception e) {
					System.out.println(e);
					continue;
				}
				g.setColor(dataColors.elementAt(i));

				try{
					if(!(data.elementAt(i) instanceof Integer)) {
						throw(new Exception("Invalid value for type number"));
					}
				} catch(Exception e) {
					System.out.println(e);
					continue;
				}

				int barLength = (data.elementAt(i)).intValue();
				g.fillOval(100, yposition, barLength, barWidth);
				g.setColor(Color.black);

				try{
					if(dataLabels.elementAt(i).isBlank()) {
						throw(new Exception("Label cannot be blank"));
					}
				} catch(Exception e){
					System.out.println(e);
					return;
				}

				g.drawString(dataLabels.elementAt(i), 20, yposition+10);
			}
		}

	public void setData(Vector<Integer> dataValues)
	{
		data = dataValues;
	}

	public void setLabels(Vector<String> labels)
	{
		dataLabels = labels;
	}

	public void setColors(Vector<Color> colors)
	{
		dataColors = colors;
	}
}
