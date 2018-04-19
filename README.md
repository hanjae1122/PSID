# PSID

The files in this repository are used to read data from The Panel Study of Income Dynamics (PSID), &ldquo;the longest running longitudinal household survey in the world&rdquo;. 

Visit the1 site at <https://psidonline.isr.umich.edu/>.

The code can be used by someone who does not have the necessary programs (STATA, SAS or SPSS) to open the .txt PSID data files but want to convert them into a more accessible format. The code provided here allows one to convert these .txt files (along with the SPSS name file that gives the variable names) into csv format.

# PSID data format

PSID data can be downloaded in different formats. Variabls specifically selected in [data center](https://simba.isr.umich.edu/default.aspx) using something like &lsquo;Variable Search&rsquo; can be downloaded in dBase Data File (DBF) format, which you can easily open in python using the appropriate module. However, most files come in the following form:

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="left" />

<col  class="left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="left">File type</th>
<th scope="col" class="left">Description</th>
</tr>
</thead>

<tbody>
<tr>
<td class="left">.do</td>
<td class="left">STATA name file</td>
</tr>


<tr>
<td class="left">.sas</td>
<td class="left">SAS name file</td>
</tr>


<tr>
<td class="left">.sps</td>
<td class="left">SPSS name file</td>
</tr>


<tr>
<td class="left">.txt</td>
<td class="left">data in raw ASCII format</td>
</tr>


<tr>
<td class="left">codebook</td>
<td class="left">coding of variable names</td>
</tr>
</tbody>
</table>

The .txt file is not in a format that can easily be read into a program, such as python or excel. Instead, it&rsquo;s in what&rsquo;s called a raw ascii format, specifically fixed format. You can read more about this [here](http://wlm.userweb.mwn.de/SPSS/wlmsrrd.htm).